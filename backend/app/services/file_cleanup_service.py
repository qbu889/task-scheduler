"""
导出文件清理服务
定时清理过期的导出文件，避免磁盘空间占用
"""
import os
import re
import glob
import logging
from datetime import datetime, timedelta
from app import db
from config import Config
from app.models.sql_export_task import SqlExportTask

logger = logging.getLogger(__name__)


class FileCleanupService:
    """文件清理服务类"""
    
    # 默认保留天数
    DEFAULT_RETENTION_DAYS = 7
    
    # 文件名格式模式：{prefix}_{YYYYMMDD_HHMMSS}[_partN].xlsx
    FILENAME_PATTERN = re.compile(
        r'^(.+?)_(\d{8}_\d{6})(?:_part\d+)?\.xlsx$'
    )
    
    @staticmethod
    def _get_configured_export_paths():
        """
        获取配置文件中指定的导出路径列表
        
        Returns:
            list: 导出路径列表（绝对路径）
        """
        # 从配置中获取导出路径
        export_path = getattr(Config, 'EXPORT_DEFAULT_PATH', './exports/')
        
        # 支持多个路径配置（用逗号分隔）
        if isinstance(export_path, str) and ',' in export_path:
            paths = [p.strip() for p in export_path.split(',')]
        elif isinstance(export_path, (list, tuple)):
            paths = list(export_path)
        else:
            paths = [str(export_path)]
        
        # 转换为绝对路径并验证
        valid_paths = []
        for path in paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.isdir(abs_path):
                valid_paths.append(abs_path)
            else:
                logger.warning(f"Configured export path does not exist: {abs_path}")
        
        logger.info(f"Found {len(valid_paths)} configured export path(s): {valid_paths}")
        return valid_paths
    
    @staticmethod
    def clean_old_files(retention_days=None):
        """
        清理超过保留天数的导出文件
        
        Args:
            retention_days (int, optional): 保留天数，默认使用配置值
            
        Returns:
            dict: 清理结果统计
        """
        if retention_days is None:
            retention_days = FileCleanupService.DEFAULT_RETENTION_DAYS
        
        logger.info(f"Starting file cleanup: retention_days={retention_days}")
        
        # 获取配置的清理路径列表
        export_paths = FileCleanupService._get_configured_export_paths()
        
        # 统计信息
        stats = {
            'total_scanned': 0,      # 扫描的文件总数
            'total_deleted': 0,      # 删除的文件总数
            'total_size_freed': 0,   # 释放的空间（字节）
            'errors': [],            # 错误列表
            'paths_cleaned': {}      # 各路径清理统计
        }
        
        # 遍历所有导出路径
        for export_path in export_paths:
            if not os.path.exists(export_path):
                logger.warning(f"Export path does not exist: {export_path}")
                continue
            
            logger.info(f"Scanning export path: {export_path}")
            
            path_stats = {
                'scanned': 0,
                'deleted': 0,
                'freed': 0
            }
            
            # 获取所有xlsx文件
            xlsx_files = glob.glob(os.path.join(export_path, '*.xlsx'))
            
            for file_path in xlsx_files:
                path_stats['scanned'] += 1
                stats['total_scanned'] += 1
                
                try:
                    # 提取文件名
                    filename = os.path.basename(file_path)
                    
                    # 验证文件名格式，避免误删
                    if not FileCleanupService._is_valid_export_file(filename):
                        logger.debug(f"Skipping non-export file: {filename}")
                        continue
                    
                    # 从文件名提取时间戳
                    timestamp = FileCleanupService._extract_timestamp(filename)
                    if not timestamp:
                        logger.debug(f"Cannot extract timestamp from: {filename}")
                        continue
                    
                    # 计算文件年龄
                    file_age = datetime.now() - timestamp
                    file_age_days = file_age.days
                    
                    # 判断是否需要清理
                    if file_age_days > retention_days:
                        file_size = os.path.getsize(file_path)
                        
                        # 删除文件
                        os.remove(file_path)
                        
                        path_stats['deleted'] += 1
                        path_stats['freed'] += file_size
                        stats['total_deleted'] += 1
                        stats['total_size_freed'] += file_size
                        
                        logger.info(f"Deleted old file: {filename} "
                                  f"(age: {file_age_days} days, size: {file_size / 1024:.2f} KB)")
                    
                except Exception as e:
                    error_msg = f"Failed to process {filename}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    stats['errors'].append(error_msg)
            
            stats['paths_cleaned'][export_path] = path_stats
        
        # 输出统计信息
        logger.info(f"File cleanup completed: "
                   f"scanned={stats['total_scanned']}, "
                   f"deleted={stats['total_deleted']}, "
                   f"freed={stats['total_size_freed'] / 1024:.2f} KB")
        
        return stats
    
    @staticmethod
    def _is_valid_export_file(filename):
        """
        验证是否为合法的导出文件
        
        规则：
        1. 必须是 .xlsx 文件
        2. 文件名必须包含 8位日期_6位时间 格式
        3. 可选包含 _partN 分片标记
        
        Args:
            filename (str): 文件名
            
        Returns:
            bool: 是否为合法的导出文件
        """
        if not filename.endswith('.xlsx'):
            return False
        
        match = FileCleanupService.FILENAME_PATTERN.match(filename)
        if not match:
            return False
        
        # 验证前缀不为空
        prefix = match.group(1)
        if not prefix:
            return False
        
        return True
    
    @staticmethod
    def _extract_timestamp(filename):
        """
        从文件名提取时间戳
        
        Args:
            filename (str): 文件名
            
        Returns:
            datetime: 提取的时间，如果提取失败返回 None
        """
        match = FileCleanupService.FILENAME_PATTERN.match(filename)
        if not match:
            return None
        
        timestamp_str = match.group(2)  # YYYYMMDD_HHMMSS
        
        try:
            # 解析时间戳
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            return timestamp
        except ValueError:
            logger.warning(f"Invalid timestamp in filename: {filename}")
            return None
    
    @staticmethod
    def cleanup_by_task_id(task_id, retention_days=None):
        """
        清理指定任务的过期文件
        
        Args:
            task_id (int): 任务ID
            retention_days (int, optional): 保留天数
            
        Returns:
            dict: 清理结果统计
        """
        task = SqlExportTask.query.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        export_path = task.export_path
        if not os.path.exists(export_path):
            logger.warning(f"Export path does not exist: {export_path}")
            return {
                'total_scanned': 0,
                'total_deleted': 0,
                'total_size_freed': 0,
                'errors': []
            }
        
        logger.info(f"Cleaning files for task {task_id}: {task.task_name}")
        
        stats = {
            'total_scanned': 0,
            'total_deleted': 0,
            'total_size_freed': 0,
            'errors': []
        }
        
        # 获取该任务的所有文件（根据filename_prefix）
        pattern = f"{task.filename_prefix}_*.xlsx"
        files = glob.glob(os.path.join(export_path, pattern))
        
        for file_path in files:
            stats['total_scanned'] += 1
            
            try:
                filename = os.path.basename(file_path)
                
                # 提取时间戳
                timestamp = FileCleanupService._extract_timestamp(filename)
                if not timestamp:
                    continue
                
                # 计算文件年龄
                file_age_days = (datetime.now() - timestamp).days
                
                # 判断是否需要清理
                if file_age_days > (retention_days or FileCleanupService.DEFAULT_RETENTION_DAYS):
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    
                    stats['total_deleted'] += 1
                    stats['total_size_freed'] += file_size
                    
                    logger.info(f"Deleted task {task_id} file: {filename}")
            
            except Exception as e:
                error_msg = f"Failed to process {file_path}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                stats['errors'].append(error_msg)
        
        logger.info(f"Task {task_id} cleanup: scanned={stats['total_scanned']}, "
                   f"deleted={stats['total_deleted']}")
        
        return stats
    
    @staticmethod
    def get_cleanup_report(retention_days=None):
        """
        获取清理报告（不实际删除文件）
        
        Args:
            retention_days (int, optional): 保留天数
            
        Returns:
            dict: 清理报告
        """
        if retention_days is None:
            retention_days = FileCleanupService.DEFAULT_RETENTION_DAYS
        
        report = {
            'retention_days': retention_days,
            'total_scanned': 0,
            'files_to_delete': [],
            'total_size_to_free': 0,
            'errors': []
        }
        
        # 获取配置的清理路径列表
        export_paths = FileCleanupService._get_configured_export_paths()
        
        for export_path in export_paths:
            if not os.path.exists(export_path):
                continue
            
            # 获取所有xlsx文件
            xlsx_files = glob.glob(os.path.join(export_path, '*.xlsx'))
            
            for file_path in xlsx_files:
                report['total_scanned'] += 1
                
                try:
                    filename = os.path.basename(file_path)
                    
                    # 验证是否为导出文件
                    if not FileCleanupService._is_valid_export_file(filename):
                        continue
                    
                    # 提取时间戳
                    timestamp = FileCleanupService._extract_timestamp(filename)
                    if not timestamp:
                        continue
                    
                    # 计算文件年龄
                    file_age_days = (datetime.now() - timestamp).days
                    
                    # 判断是否需要清理
                    if file_age_days > retention_days:
                        file_size = os.path.getsize(file_path)
                        report['files_to_delete'].append({
                            'file_path': file_path,
                            'filename': filename,
                            'file_size': file_size,
                            'file_age_days': file_age_days,
                            'timestamp': timestamp.isoformat()
                        })
                        report['total_size_to_free'] += file_size
                
                except Exception as e:
                    error_msg = f"Failed to analyze {file_path}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    report['errors'].append(error_msg)
        
        logger.info(f"Cleanup report: {len(report['files_to_delete'])} files to delete, "
                   f"size: {report['total_size_to_free'] / 1024:.2f} KB")
        
        return report


# 创建服务实例
file_cleanup_service = FileCleanupService()
