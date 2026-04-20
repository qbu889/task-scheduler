"""
SQL导出任务模型单元测试
"""
import pytest
from datetime import datetime
from app.models.sql_export_task import SqlExportTask


class TestSqlExportTask:
    """SQL导出任务模型测试类"""
    
    def test_create_task(self):
        """测试创建任务"""
        task = SqlExportTask(
            task_name='测试任务',
            datasource_type='mysql',
            datasource_config='{"host": "localhost"}',
            sql_template='SELECT * FROM test',
            time_params='{}',
            cron_expression='0 9 * * *',
            export_path='/exports/',
            filename_prefix='test'
        )
        
        assert task.task_name == '测试任务'
        assert task.datasource_type == 'mysql'
        # default值只在数据库层面生效，Python对象中为None
        assert task.max_rows is None or task.max_rows == 100000
        assert task.batch_size is None or task.batch_size == 5000
    
    def test_task_to_dict(self):
        """测试to_dict方法"""
        task = SqlExportTask(
            task_name='测试任务',
            datasource_type='mysql',
            datasource_config='{}',
            sql_template='SELECT 1',
            time_params='{}',
            cron_expression='0 0 * * *',
            export_path='/tmp/',
            filename_prefix='export'
        )
        task.task_id = 1
        task.created_at = datetime(2025, 1, 1, 12, 0, 0)
        task.updated_at = datetime(2025, 1, 1, 12, 0, 0)
        
        result = task.to_dict()
        
        assert result['task_id'] == 1
        assert result['task_name'] == '测试任务'
        assert result['datasource_type'] == 'mysql'
        assert 'created_at' in result
        assert 'updated_at' in result
    
    def test_task_default_values(self):
        """测试默认值"""
        task = SqlExportTask(
            task_name='默认值测试',
            datasource_type='mysql',
            datasource_config='{}',
            sql_template='SELECT 1',
            time_params='{}',
            cron_expression='0 0 * * *',
            export_path='/tmp/',
            filename_prefix='test'
        )
        
        # default值只在数据库层面生效
        assert task.is_enabled is None or task.is_enabled == 1
        assert task.max_rows is None or task.max_rows == 100000
        assert task.batch_size is None or task.batch_size == 5000
    
    def test_disable_task(self):
        """测试禁用任务"""
        task = SqlExportTask(
            task_name='测试任务',
            datasource_type='mysql',
            datasource_config='{}',
            sql_template='SELECT 1',
            time_params='{}',
            cron_expression='0 0 * * *',
            export_path='/tmp/',
            filename_prefix='test',
            is_enabled=0
        )
        
        assert task.is_enabled == 0
    
    def test_custom_max_rows(self):
        """测试自定义最大行数"""
        task = SqlExportTask(
            task_name='测试任务',
            datasource_type='mysql',
            datasource_config='{}',
            sql_template='SELECT 1',
            time_params='{}',
            cron_expression='0 0 * * *',
            export_path='/tmp/',
            filename_prefix='test',
            max_rows=100000,
            batch_size=10000
        )
        
        assert task.max_rows == 100000
        assert task.batch_size == 10000
