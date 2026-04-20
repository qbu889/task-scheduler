"""
SQL导出日志模型单元测试
"""
import pytest
from datetime import datetime
from app.models.sql_export_log import SqlExportLog


class TestSqlExportLog:
    """SQL导出日志模型测试类"""
    
    def test_create_success_log(self):
        """测试创建成功日志"""
        log = SqlExportLog(
            task_id=1,
            start_time=datetime(2025, 1, 1, 10, 0, 0),
            end_time=datetime(2025, 1, 1, 10, 5, 30),
            status='success',
            record_count=1000,
            file_path='/exports/test.xlsx',
            file_size=102400,
            duration_seconds=330.5
        )
        
        assert log.task_id == 1
        assert log.status == 'success'
        assert log.record_count == 1000
        assert log.duration_seconds == 330.5
    
    def test_create_failed_log(self):
        """测试创建失败日志"""
        log = SqlExportLog(
            task_id=1,
            start_time=datetime(2025, 1, 1, 10, 0, 0),
            status='failed',
            error_message='数据库连接失败'
        )
        
        assert log.task_id == 1
        assert log.status == 'failed'
        assert log.error_message == '数据库连接失败'
        # default值只在数据库层面生效
        assert log.record_count is None or log.record_count == 0
    
    def test_log_to_dict(self):
        """测试to_dict方法"""
        log = SqlExportLog(
            task_id=1,
            start_time=datetime(2025, 1, 1, 10, 0, 0),
            end_time=datetime(2025, 1, 1, 10, 5, 30),
            status='success',
            record_count=500,
            file_path='/exports/test.xlsx',
            file_size=51200,
            duration_seconds=300.0
        )
        log.log_id = 1
        log.created_at = datetime(2025, 1, 1, 10, 5, 30)
        
        result = log.to_dict()
        
        assert result['log_id'] == 1
        assert result['task_id'] == 1
        assert result['status'] == 'success'
        assert result['record_count'] == 500
        assert 'start_time' in result
        assert 'end_time' in result
    
    def test_log_without_end_time(self):
        """测试没有结束时间的日志（执行中）"""
        log = SqlExportLog(
            task_id=1,
            start_time=datetime(2025, 1, 1, 10, 0, 0),
            status='running'
        )
        
        assert log.end_time is None
        assert log.duration_seconds is None
    
    def test_log_default_values(self):
        """测试默认值"""
        log = SqlExportLog(
            task_id=1,
            start_time=datetime.now(),
            status='success'
        )
        
        # default值只在数据库层面生效
        assert log.record_count is None or log.record_count == 0
        assert log.file_size is None
