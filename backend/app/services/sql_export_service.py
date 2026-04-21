"""
SQL导出任务管理服务
"""
from app import db
from app.models.sql_export_task import SqlExportTask
from app.models.sql_export_log import SqlExportLog
from app.utils.time_calculator import calculate_all_time_params
from app.services.sql_executor import execute_sql
from app.services.excel_exporter import export_to_excel, get_file_size
from app.utils.crypto import encrypt
from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)


class SqlExportService:
    """SQL导出任务服务类"""
    
    @staticmethod
    def create_task(config):
        """
        创建新的导出任务
        
        Args:
            config (dict): 任务配置
            
        Returns:
            SqlExportTask: 创建的任务对象
        """
        try:
            logger.info(f"Creating task: name={config.get('task_name')}, datasource_type={config.get('datasource_type')}")
            
            # 加密数据源密码
            datasource_config = config.get('datasource_config', {})
            if 'password' in datasource_config and datasource_config['password']:
                logger.debug("Encrypting datasource password")
                datasource_config['password'] = encrypt(datasource_config['password'])
            
            task = SqlExportTask(
                task_name=config.get('task_name'),
                datasource_type=config.get('datasource_type', 'mysql'),
                datasource_config=json.dumps(datasource_config),
                sql_template=config.get('sql_template'),
                time_params=json.dumps(config.get('time_params', {})),
                cron_expression=config.get('cron_expression', '0 0 2 * * *'),
                export_path=config.get('export_path', './exports/'),
                filename_prefix=config.get('filename_prefix', 'export'),
                max_rows=config.get('max_rows', 100000),
                batch_size=config.get('batch_size', 5000),
                is_enabled=config.get('is_enabled', 1),
                description=config.get('description', '')
            )
            
            db.session.add(task)
            db.session.commit()
            
            logger.info(f"Task created successfully: task_id={task.task_id}, name={task.task_name}")
            return task
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create task: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def update_task(task_id, config):
        """
        更新任务配置
        
        Args:
            task_id (int): 任务ID
            config (dict): 更新的配置
            
        Returns:
            SqlExportTask: 更新后的任务对象
        """
        try:
            task = SqlExportTask.query.get(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            
            # 更新字段
            if 'task_name' in config:
                task.task_name = config['task_name']
            if 'sql_template' in config:
                task.sql_template = config['sql_template']
            if 'time_params' in config:
                task.time_params = json.dumps(config['time_params'])
            if 'cron_expression' in config:
                task.cron_expression = config['cron_expression']
            if 'export_path' in config:
                task.export_path = config['export_path']
            if 'filename_prefix' in config:
                task.filename_prefix = config['filename_prefix']
            if 'max_rows' in config:
                task.max_rows = config['max_rows']
            if 'batch_size' in config:
                task.batch_size = config['batch_size']
            if 'description' in config:
                task.description = config['description']
            
            # 如果更新了数据源配置，需要重新加密密码
            if 'datasource_config' in config:
                datasource_config = config['datasource_config']
                # 如果密码为空或是掩码（'***'），则保留原密码
                if 'password' in datasource_config:
                    if datasource_config['password'] and datasource_config['password'] != '***':
                        datasource_config['password'] = encrypt(datasource_config['password'])
                    else:
                        # 保留原有密码
                        original_config = json.loads(task.datasource_config)
                        datasource_config['password'] = original_config.get('password', '')
                task.datasource_config = json.dumps(datasource_config)
            
            db.session.commit()
            logger.info(f"Task updated: {task.task_name} (ID: {task.task_id})")
            return task
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update task: {str(e)}")
            raise
    
    @staticmethod
    def delete_task(task_id):
        """
        删除任务
        
        Args:
            task_id (int): 任务ID
        """
        try:
            task = SqlExportTask.query.get(task_id)
            if not task:
                raise ValueError(f"Task not found: {task_id}")
            
            db.session.delete(task)
            db.session.commit()
            logger.info(f"Task deleted: ID {task_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete task: {str(e)}")
            raise
    
    @staticmethod
    def enable_task(task_id):
        """启用任务"""
        task = SqlExportTask.query.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.is_enabled = 1
        db.session.commit()
        logger.info(f"Task enabled: ID {task_id}")
        return task
    
    @staticmethod
    def disable_task(task_id):
        """停用任务"""
        task = SqlExportTask.query.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.is_enabled = 0
        db.session.commit()
        logger.info(f"Task disabled: ID {task_id}")
        return task
    
    @staticmethod
    def get_task_list(page=1, page_size=10, is_enabled=None, task_name=None):
        """
        获取任务列表
        
        Args:
            page (int): 页码
            page_size (int): 每页数量
            is_enabled (int): 筛选条件（0-停用，1-启用，None-全部）
            task_name (str): 任务名称搜索（模糊匹配）
            
        Returns:
            tuple: (tasks, total, page, page_size)
        """
        query = SqlExportTask.query
        
        if is_enabled is not None:
            query = query.filter_by(is_enabled=is_enabled)
        
        if task_name:
            query = query.filter(SqlExportTask.task_name.like(f'%{task_name}%'))
        
        query = query.order_by(SqlExportTask.created_at.desc())
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return pagination.items, pagination.total, page, page_size
    
    @staticmethod
    def get_task_detail(task_id):
        """获取任务详情"""
        task = SqlExportTask.query.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        return task
    
    @staticmethod
    def execute_task(task_id, override_time_params=None):
        """
        执行导出任务
        
        Args:
            task_id (int): 任务ID
            override_time_params (dict): 覆盖的时间参数（可选）
            
        Returns:
            dict: 执行结果
        """
        import time
        start_time = time.time()
        
        task = SqlExportTask.query.get(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        logger.info(f"Starting task execution: task_id={task_id}, name={task.task_name}")
        
        # 创建日志记录
        log = SqlExportLog(
            task_id=task_id,
            start_time=datetime.now(),
            status='running'
        )
        db.session.add(log)
        db.session.commit()
        
        try:
            # 获取数据源配置
            datasource_config = task.get_datasource_config()
            datasource_config['type'] = task.datasource_type
            logger.debug(f"Datasource type: {task.datasource_type}, host: {datasource_config.get('host')}")
            
            # 计算时间参数
            if override_time_params:
                time_params = override_time_params
                logger.info(f"Using override time params: {list(time_params.keys())}")
            else:
                time_params_config = task.get_time_params()
                time_params = calculate_all_time_params(time_params_config)
                logger.debug(f"Calculated time params: {time_params}")
            
            # 执行SQL查询（使用分页查询提升性能）
            logger.info(f"Executing SQL query for task {task_id}")
            query_start = time.time()
            
            # 替换SQL占位符，生成最终SQL（用于日志记录）
            from app.services.sql_executor import replace_sql_placeholders
            final_sql = replace_sql_placeholders(task.sql_template, time_params)
            
            # 根据任务配置选择查询方式
            if task.max_rows and task.max_rows > 0:
                # 使用分页查询，适合大数据量
                from app.services.sql_executor import execute_sql_paginated
                df, record_count = execute_sql_paginated(
                    datasource_config=datasource_config,
                    sql_template=task.sql_template,
                    time_params=time_params,
                    batch_size=task.batch_size,
                    max_rows=task.max_rows
                )
            else:
                # 使用普通查询，适合小数据量
                df, record_count, _ = execute_sql(
                    datasource_config=datasource_config,
                    sql_template=task.sql_template,
                    time_params=time_params,
                    batch_size=task.batch_size
                )
            
            query_duration = time.time() - query_start
            logger.info(f"SQL query completed: {record_count} rows fetched in {query_duration:.2f}s")
            
            if df.empty:
                logger.warning(f"Query returned no data for task {task_id}")
                log.status = 'success'
                log.record_count = 0
                log.final_sql = final_sql
                log.end_time = datetime.now()
                log.duration_seconds = (log.end_time - log.start_time).total_seconds()
                db.session.commit()
                
                return {
                    'success': True,
                    'message': '查询成功，但无数据',
                    'record_count': 0,
                    'file_paths': []
                }
            
            # 导出Excel
            logger.info(f"Exporting {record_count} rows to Excel")
            export_start = time.time()
            
            file_paths = export_to_excel(
                df=df,
                filepath=task.export_path,
                filename_prefix=task.filename_prefix,
                max_rows_per_file=50000
            )
            
            export_duration = time.time() - export_start
            logger.info(f"Excel export completed: {len(file_paths)} files created in {export_duration:.2f}s")
            
            # 更新日志
            log.status = 'success'
            log.record_count = record_count
            log.final_sql = final_sql
            log.file_path = ';'.join(file_paths) if file_paths else ''
            log.file_size = sum(get_file_size(fp) for fp in file_paths)
            log.end_time = datetime.now()
            log.duration_seconds = (log.end_time - log.start_time).total_seconds()
            
            db.session.commit()
            
            total_duration = time.time() - start_time
            logger.info(f"Task completed successfully: task_id={task_id}, rows={record_count}, "
                       f"files={len(file_paths)}, duration={total_duration:.2f}s")
            
            return {
                'success': True,
                'message': '导出成功',
                'record_count': record_count,
                'file_paths': file_paths
            }
            
        except Exception as e:
            total_duration = time.time() - start_time
            logger.error(f"Task execution failed: task_id={task_id}, duration={total_duration:.2f}s, error={str(e)}", 
                        exc_info=True)
            
            # 更新日志为失败
            log.status = 'failed'
            log.error_message = str(e)
            log.end_time = datetime.now()
            log.duration_seconds = (log.end_time - log.start_time).total_seconds()
            
            db.session.commit()
            
            raise
    
    @staticmethod
    def get_execution_logs(task_id=None, status=None, page=1, page_size=20):
        """
        获取执行日志
        
        Args:
            task_id (int): 任务ID（可选）
            status (str): 执行状态（可选，'success' 或 'failed'）
            page (int): 页码
            page_size (int): 每页数量
            
        Returns:
            tuple: (logs, total, page, page_size)
        """
        query = SqlExportLog.query
        
        if task_id:
            query = query.filter_by(task_id=task_id)
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(SqlExportLog.start_time.desc())
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return pagination.items, pagination.total, page, page_size


# 创建服务实例
sql_export_service = SqlExportService()
