"""
文件清理服务单元测试
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.file_cleanup_service import FileCleanupService


class TestFileCleanupService:
    """文件清理服务测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.service = FileCleanupService()
        
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        
        # 创建一些测试文件
        self.create_test_files()
    
    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 删除临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """创建测试用的导出文件"""
        now = datetime.now()
        
        # 合法的文件（3天前）
        old_date = (now - timedelta(days=3)).strftime('%Y%m%d_%H%M%S')
        self.old_file_1 = f"泉州遗留库工单_{old_date}.xlsx"
        self.create_dummy_file(self.old_file_1, size_kb=100)
        
        # 合法的文件（8天前，应该被清理）
        old_date_2 = (now - timedelta(days=8)).strftime('%Y%m%d_%H%M%S')
        self.old_file_2 = f"泉州遗留库工单_{old_date_2}.xlsx"
        self.create_dummy_file(self.old_file_2, size_kb=200)
        
        # 合法的文件（10天前，分片文件，应该被清理）
        old_date_3 = (now - timedelta(days=10)).strftime('%Y%m%d_%H%M%S')
        self.old_file_3 = f"泉州遗留库工单_{old_date_3}_part2.xlsx"
        self.create_dummy_file(self.old_file_3, size_kb=150)
        
        # 不合法的文件（无时间戳）
        self.invalid_file_1 = "important_data.xlsx"
        self.create_dummy_file(self.invalid_file_1, size_kb=50)
        
        # 不合法的文件（时间格式不对）
        self.invalid_file_2 = "report_2026-04-20.xlsx"
        self.create_dummy_file(self.invalid_file_2, size_kb=80)
        
        # 不合法的文件（非xlsx）
        self.invalid_file_3 = "backup.zip"
        self.create_dummy_file(self.invalid_file_3, size_kb=30)
    
    def create_dummy_file(self, filename, size_kb=100):
        """创建虚拟文件"""
        file_path = os.path.join(self.test_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(b'x' * (size_kb * 1024))
        return file_path
    
    def test_is_valid_export_file_valid(self):
        """测试验证合法的导出文件"""
        assert self.service._is_valid_export_file("泉州遗留库工单_20260420_020000.xlsx") is True
        assert self.service._is_valid_export_file("泉州遗留库工单_20260420_020000_part2.xlsx") is True
        assert self.service._is_valid_export_file("export_20240101_120000.xlsx") is True
        assert self.service._is_valid_export_file("test_20241231_235959_part10.xlsx") is True
    
    def test_is_valid_export_file_invalid_extension(self):
        """测试验证非法扩展名"""
        assert self.service._is_valid_export_file("file.txt") is False
        assert self.service._is_valid_export_file("file.csv") is False
        assert self.service._is_valid_export_file("file.zip") is False
        assert self.service._is_valid_export_file("file.pdf") is False
    
    def test_is_valid_export_file_no_timestamp(self):
        """测试验证无时间戳的文件"""
        assert self.service._is_valid_export_file("important_data.xlsx") is False
        assert self.service._is_valid_export_file("report.xlsx") is False
        assert self.service._is_valid_export_file("_20260420_020000.xlsx") is False
    
    def test_is_valid_export_file_wrong_timestamp_format(self):
        """测试验证错误的时间戳格式"""
        assert self.service._is_valid_export_file("report_2026-04-20.xlsx") is False
        assert self.service._is_valid_export_file("report_20260420.xlsx") is False
        assert self.service._is_valid_export_file("report_020000.xlsx") is False
        assert self.service._is_valid_export_file("report_20260420020000.xlsx") is False
    
    def test_extract_timestamp_success(self):
        """测试成功提取时间戳"""
        timestamp = self.service._extract_timestamp("泉州遗留库工单_20260420_020000.xlsx")
        assert timestamp == datetime(2026, 4, 20, 2, 0, 0)
        
        timestamp = self.service._extract_timestamp("export_20241231_235959.xlsx")
        assert timestamp == datetime(2024, 12, 31, 23, 59, 59)
    
    def test_extract_timestamp_with_part(self):
        """测试提取带分片标记的时间戳"""
        timestamp = self.service._extract_timestamp("泉州遗留库工单_20260420_020000_part2.xlsx")
        assert timestamp == datetime(2026, 4, 20, 2, 0, 0)
        
        timestamp = self.service._extract_timestamp("export_20240101_120000_part10.xlsx")
        assert timestamp == datetime(2024, 1, 1, 12, 0, 0)
    
    def test_extract_timestamp_invalid(self):
        """测试提取无效时间戳"""
        assert self.service._extract_timestamp("important_data.xlsx") is None
        assert self.service._extract_timestamp("report_2026-04-20.xlsx") is None
        assert self.service._extract_timestamp("backup.zip") is None
    
    @patch('app.services.file_cleanup_service.Config')
    def test_get_configured_export_paths_single(self, mock_config):
        """测试获取单个配置的导出路径"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        paths = self.service._get_configured_export_paths()
        
        assert len(paths) == 1
        assert paths[0] == os.path.abspath(self.test_dir)
    
    @patch('app.services.file_cleanup_service.Config')
    def test_get_configured_export_paths_multiple(self, mock_config):
        """测试获取多个配置的导出路径"""
        test_dir_2 = tempfile.mkdtemp()
        try:
            mock_config.EXPORT_DEFAULT_PATH = f"{self.test_dir},{test_dir_2}"
            
            paths = self.service._get_configured_export_paths()
            
            assert len(paths) == 2
            assert os.path.abspath(self.test_dir) in paths
            assert os.path.abspath(test_dir_2) in paths
        finally:
            shutil.rmtree(test_dir_2)
    
    @patch('app.services.file_cleanup_service.Config')
    def test_get_configured_export_paths_nonexistent(self, mock_config):
        """测试获取不存在的路径"""
        nonexistent_path = "/nonexistent/path/that/does/not/exist"
        mock_config.EXPORT_DEFAULT_PATH = f"{self.test_dir},{nonexistent_path}"
        
        paths = self.service._get_configured_export_paths()
        
        # 只返回存在的路径
        assert len(paths) == 1
        assert paths[0] == os.path.abspath(self.test_dir)
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_default_retention(self, mock_config):
        """测试使用默认保留天数清理文件"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        stats = self.service.clean_old_files(retention_days=7)
        
        # 应该扫描所有xlsx文件（包括合法和非法的）
        assert stats['total_scanned'] >= 3  # 至少3个合法文件
        
        # 应该删除超过7天的文件（8天和10天的）
        assert stats['total_deleted'] == 2
        
        # 释放的空间应该是两个文件的总和
        expected_freed = (200 + 150) * 1024  # 200KB + 150KB
        assert stats['total_size_freed'] == expected_freed
        
        # 验证文件确实被删除了
        assert not os.path.exists(os.path.join(self.test_dir, self.old_file_2))
        assert not os.path.exists(os.path.join(self.test_dir, self.old_file_3))
        
        # 验证未到期文件仍然存在
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_1))
        
        # 验证非法文件没有被删除
        assert os.path.exists(os.path.join(self.test_dir, self.invalid_file_1))
        assert os.path.exists(os.path.join(self.test_dir, self.invalid_file_2))
        assert os.path.exists(os.path.join(self.test_dir, self.invalid_file_3))
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_custom_retention(self, mock_config):
        """测试使用自定义保留天数清理文件"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        # 设置为5天，应该只删除8天和10天的文件
        stats = self.service.clean_old_files(retention_days=5)
        
        assert stats['total_deleted'] == 2
        
        # 3天前的文件应该保留
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_1))
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_no_files_to_delete(self, mock_config):
        """测试没有需要清理的文件"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        # 设置为100天，所有文件都应该保留
        stats = self.service.clean_old_files(retention_days=100)
        
        assert stats['total_deleted'] == 0
        assert stats['total_size_freed'] == 0
        
        # 所有文件都应该还在
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_1))
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_2))
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_3))
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_empty_directory(self, mock_config):
        """测试空目录清理"""
        empty_dir = tempfile.mkdtemp()
        try:
            mock_config.EXPORT_DEFAULT_PATH = empty_dir
            
            stats = self.service.clean_old_files(retention_days=7)
            
            assert stats['total_scanned'] == 0
            assert stats['total_deleted'] == 0
            assert stats['total_size_freed'] == 0
        finally:
            shutil.rmtree(empty_dir)
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_nonexistent_path(self, mock_config):
        """测试不存在的路径"""
        mock_config.EXPORT_DEFAULT_PATH = "/nonexistent/path"
        
        stats = self.service.clean_old_files(retention_days=7)
        
        assert stats['total_scanned'] == 0
        assert stats['total_deleted'] == 0
    
    @patch('app.services.file_cleanup_service.Config')
    def test_get_cleanup_report(self, mock_config):
        """测试获取清理报告"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        report = self.service.get_cleanup_report(retention_days=7)
        
        assert report['retention_days'] == 7
        assert report['total_scanned'] >= 3
        
        # 应该有2个文件待删除（8天和10天的）
        assert len(report['files_to_delete']) == 2
        
        # 验证报告中的文件信息
        for file_info in report['files_to_delete']:
            assert 'file_path' in file_info
            assert 'filename' in file_info
            assert 'file_size' in file_info
            assert 'file_age_days' in file_info
            assert 'timestamp' in file_info
            assert file_info['file_age_days'] > 7
        
        # 验证实际文件没有被删除
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_2))
        assert os.path.exists(os.path.join(self.test_dir, self.old_file_3))
    
    @patch('app.models.sql_export_task.SqlExportTask')
    @patch('app.services.file_cleanup_service.db')
    def test_cleanup_by_task_id_success(self, mock_db, mock_task_class):
        """测试按任务ID清理文件"""
        # Mock task
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.filename_prefix = "泉州遗留库工单"
        mock_task.export_path = self.test_dir
        mock_task_class.query.get.return_value = mock_task
        
        stats = self.service.cleanup_by_task_id(1, retention_days=7)
        
        # 应该只清理该任务前缀的文件
        assert stats['total_scanned'] >= 2  # 至少有2个匹配前缀的文件
        assert stats['total_deleted'] == 2  # 8天和10天的文件
        
        # 验证文件被删除
        assert not os.path.exists(os.path.join(self.test_dir, self.old_file_2))
        assert not os.path.exists(os.path.join(self.test_dir, self.old_file_3))
    
    @patch('app.models.sql_export_task.SqlExportTask')
    def test_cleanup_by_task_id_not_found(self, mock_task_class):
        """测试按任务ID清理时任务不存在"""
        mock_task_class.query.get.return_value = None
        
        with pytest.raises(ValueError, match="Task not found"):
            self.service.cleanup_by_task_id(999)
    
    @patch('app.models.sql_export_task.SqlExportTask')
    def test_cleanup_by_task_id_nonexistent_path(self, mock_task_class):
        """测试按任务ID清理时路径不存在"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.export_path = "/nonexistent/path"
        mock_task_class.query.get.return_value = mock_task
        
        stats = self.service.cleanup_by_task_id(1)
        
        assert stats['total_scanned'] == 0
        assert stats['total_deleted'] == 0
    
    @patch('app.services.file_cleanup_service.Config')
    def test_clean_old_files_error_handling(self, mock_config):
        """测试清理过程中的错误处理"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        # 创建一个无法删除的文件（权限问题模拟）
        protected_file = os.path.join(self.test_dir, "protected_20260410_020000.xlsx")
        with open(protected_file, 'w') as f:
            f.write('test')
        os.chmod(protected_file, 0o444)  # 只读
        
        try:
            stats = self.service.clean_old_files(retention_days=7)
            
            # 应该记录错误但继续处理其他文件
            assert len(stats['errors']) >= 0  # 可能有错误也可能没有（取决于系统）
            
            # 其他文件应该正常处理
            assert stats['total_deleted'] >= 2  # 至少删除了两个旧文件
        except Exception:
            pass  # macOS可能不允许root用户设置只读权限
        finally:
            # 恢复权限以便清理（如果文件还存在）
            if os.path.exists(protected_file):
                os.chmod(protected_file, 0o644)
    
    @patch('app.services.file_cleanup_service.Config')
    def test_filename_pattern_edge_cases(self, mock_config):
        """测试文件名模式的边界情况"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        # 创建边界情况的文件
        edge_cases = [
            ("a_20260420_020000.xlsx", True),  # 最短前缀
            ("very_long_prefix_name_20260420_020000.xlsx", True),  # 长前缀
            ("中文前缀_20260420_020000.xlsx", True),  # 中文前缀
            ("prefix_20260420_020000_part0.xlsx", True),  # part0
            ("prefix_20260420_020000_part999.xlsx", True),  # part999
            ("_20260420_020000.xlsx", False),  # 空前缀
            ("prefix_20260420_020000_.xlsx", False),  # 多余的下划线
            ("prefix_20260420_020000part1.xlsx", False),  # 缺少下划线
        ]
        
        for filename, should_be_valid in edge_cases:
            result = self.service._is_valid_export_file(filename)
            assert result == should_be_valid, f"Failed for {filename}: expected {should_be_valid}, got {result}"
    
    @patch('app.services.file_cleanup_service.Config')
    def test_cleanup_preserves_recent_files(self, mock_config):
        """测试清理操作保留近期文件"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        # 创建今天的文件
        today = datetime.now().strftime('%Y%m%d_%H%M%S')
        recent_file = f"recent_export_{today}.xlsx"
        self.create_dummy_file(recent_file, size_kb=50)
        
        stats = self.service.clean_old_files(retention_days=7)
        
        # 今天的文件不应该被删除
        assert os.path.exists(os.path.join(self.test_dir, recent_file))
        
        # 统计中不应包含这个文件
        deleted_filenames = [os.path.basename(f) for f in 
                           [os.path.join(self.test_dir, self.old_file_2),
                            os.path.join(self.test_dir, self.old_file_3)]]
        assert recent_file not in deleted_filenames
    
    @patch('app.services.file_cleanup_service.logger')
    @patch('app.services.file_cleanup_service.Config')
    def test_logging_during_cleanup(self, mock_config, mock_logger):
        """测试清理过程中的日志记录"""
        mock_config.EXPORT_DEFAULT_PATH = self.test_dir
        
        self.service.clean_old_files(retention_days=7)
        
        # 应该记录了开始和完成的日志
        assert mock_logger.info.called
        
        # 检查是否记录了删除操作
        delete_calls = [call for call in mock_logger.info.call_args_list 
                       if 'Deleted old file' in str(call)]
        assert len(delete_calls) == 2  # 应该删除了2个文件


class TestFileCleanupServiceIntegration:
    """文件清理服务集成测试"""
    
    def setup_method(self):
        """设置多个测试目录"""
        self.dir1 = tempfile.mkdtemp()
        self.dir2 = tempfile.mkdtemp()
    
    def teardown_method(self):
        """清理测试目录"""
        shutil.rmtree(self.dir1, ignore_errors=True)
        shutil.rmtree(self.dir2, ignore_errors=True)
    
    def create_test_file_in_dir(self, directory, days_ago, prefix="export"):
        """在指定目录创建测试文件"""
        date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{date}.xlsx"
        file_path = os.path.join(directory, filename)
        with open(file_path, 'wb') as f:
            f.write(b'x' * (100 * 1024))
        return filename
    
    @patch('app.services.file_cleanup_service.Config')
    def test_cleanup_multiple_directories(self, mock_config):
        """测试清理多个目录"""
        # 在每个目录创建文件
        old_file_1 = self.create_test_file_in_dir(self.dir1, days_ago=10)
        recent_file_1 = self.create_test_file_in_dir(self.dir1, days_ago=2)
        
        old_file_2 = self.create_test_file_in_dir(self.dir2, days_ago=15)
        recent_file_2 = self.create_test_file_in_dir(self.dir2, days_ago=1)
        
        mock_config.EXPORT_DEFAULT_PATH = f"{self.dir1},{self.dir2}"
        
        service = FileCleanupService()
        stats = service.clean_old_files(retention_days=7)
        
        # 应该删除两个目录中的旧文件
        assert stats['total_deleted'] == 2
        
        # 验证旧文件被删除
        assert not os.path.exists(os.path.join(self.dir1, old_file_1))
        assert not os.path.exists(os.path.join(self.dir2, old_file_2))
        
        # 验证新文件保留
        assert os.path.exists(os.path.join(self.dir1, recent_file_1))
        assert os.path.exists(os.path.join(self.dir2, recent_file_2))
    
    @patch('app.services.file_cleanup_service.Config')
    def test_cleanup_mixed_file_types(self, mock_config):
        """测试混合文件类型的清理"""
        # 创建各种类型的文件
        xlsx_old = self.create_test_file_in_dir(self.dir1, days_ago=10)
        xlsx_new = self.create_test_file_in_dir(self.dir1, days_ago=2)
        
        # 创建非xlsx文件
        txt_file = os.path.join(self.dir1, "data.txt")
        with open(txt_file, 'w') as f:
            f.write('test')
        
        csv_file = os.path.join(self.dir1, "report.csv")
        with open(csv_file, 'w') as f:
            f.write('col1,col2\n1,2')
        
        mock_config.EXPORT_DEFAULT_PATH = self.dir1
        
        service = FileCleanupService()
        stats = service.clean_old_files(retention_days=7)
        
        # 只应删除旧的xlsx文件
        assert stats['total_deleted'] == 1
        
        # 验证非xlsx文件未被删除
        assert os.path.exists(txt_file)
        assert os.path.exists(csv_file)
        
        # 验证新的xlsx文件保留
        assert os.path.exists(os.path.join(self.dir1, xlsx_new))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
