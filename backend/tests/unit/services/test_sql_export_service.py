"""
SQL导出服务单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
import json

from app.services.sql_export_service import SqlExportService


class TestSqlExportService:
    """SQL导出服务测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.service = SqlExportService()
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.encrypt')
    def test_create_task_success(self, mock_encrypt, mock_db):
        """测试创建任务成功"""
        mock_encrypt.return_value = 'encrypted_password'
        
        config = {
            'task_name': '测试任务',
            'datasource_type': 'mysql',
            'datasource_config': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'password': '12345678',
                'database': 'test_db'
            },
            'sql_template': 'SELECT * FROM test_table',
            'time_params': {'start_time': 'yesterday', 'end_time': 'today'},
            'cron_expression': '0 0 2 * * *',
            'export_path': './exports/',
            'filename_prefix': 'export',
            'max_rows': 100000,
            'batch_size': 5000,
            'is_enabled': 1,
            'description': '测试描述'
        }
        
        # Mock task对象
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.task_name = '测试任务'
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        with patch('app.models.sql_export_task.SqlExportTask', return_value=mock_task):
            result = self.service.create_task(config)
            
            assert result == mock_task
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()
            mock_encrypt.assert_called_once_with('12345678')
    
    @patch('app.services.sql_export_service.db')
    def test_create_task_without_password(self, mock_db):
        """测试创建任务（无密码）"""
        config = {
            'task_name': '测试任务',
            'datasource_type': 'mysql',
            'datasource_config': {
                'host': '127.0.0.1',
                'port': 3306,
                'user': 'root',
                'database': 'test_db'
            },
            'sql_template': 'SELECT * FROM test_table',
            'time_params': {},
            'cron_expression': '0 0 2 * * *'
        }
        
        mock_task = Mock()
        mock_task.task_id = 1
        
        with patch('app.models.sql_export_task.SqlExportTask', return_value=mock_task):
            result = self.service.create_task(config)
            
            assert result == mock_task
    
    @patch('app.services.sql_export_service.db')
    def test_create_task_exception(self, mock_db):
        """测试创建任务异常"""
        mock_db.session.rollback = Mock()
        mock_db.session.add = Mock(side_effect=Exception("Database error"))
        
        config = {
            'task_name': '测试任务',
            'datasource_type': 'mysql',
            'datasource_config': {},
            'sql_template': 'SELECT * FROM test_table',
            'time_params': {},
            'cron_expression': '0 0 2 * * *'
        }
        
        with pytest.raises(Exception):
            self.service.create_task(config)
        
        mock_db.session.rollback.assert_called_once()
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_update_task_success(self, mock_task_class, mock_db):
        """测试更新任务成功"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.task_name = '原任务名'
        mock_task.datasource_config = '{}'
        mock_task_class.query.get.return_value = mock_task
        
        update_config = {
            'task_name': '新任务名',
            'sql_template': 'SELECT * FROM new_table',
            'cron_expression': '0 0 3 * * *'
        }
        
        result = self.service.update_task(1, update_config)
        
        assert result.task_name == '新任务名'
        assert result.sql_template == 'SELECT * FROM new_table'
        assert result.cron_expression == '0 0 3 * * *'
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_update_task_not_found(self, mock_task_class, mock_db):
        """测试更新任务不存在"""
        mock_task_class.query.get.return_value = None
        
        with pytest.raises(ValueError, match="Task not found"):
            self.service.update_task(999, {})
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    @patch('app.services.sql_export_service.encrypt')
    def test_update_task_with_datasource(self, mock_encrypt, mock_task_class, mock_db):
        """测试更新任务数据源配置"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        mock_encrypt.return_value = 'new_encrypted_password'
        
        update_config = {
            'datasource_config': {
                'host': '192.168.1.100',
                'password': 'new_password'
            }
        }
        
        self.service.update_task(1, update_config)
        
        mock_encrypt.assert_called_once_with('new_password')
        assert mock_task.datasource_config is not None
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_delete_task_success(self, mock_task_class, mock_db):
        """测试删除任务成功"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        
        self.service.delete_task(1)
        
        mock_db.session.delete.assert_called_once_with(mock_task)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_delete_task_not_found(self, mock_task_class, mock_db):
        """测试删除任务不存在"""
        mock_task_class.query.get.return_value = None
        
        with pytest.raises(ValueError, match="Task not found"):
            self.service.delete_task(999)
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_enable_task(self, mock_task_class, mock_db):
        """测试启用任务"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.is_enabled = 0
        mock_task_class.query.get.return_value = mock_task
        
        result = self.service.enable_task(1)
        
        assert result.is_enabled == 1
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_disable_task(self, mock_task_class, mock_db):
        """测试停用任务"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.is_enabled = 1
        mock_task_class.query.get.return_value = mock_task
        
        result = self.service.disable_task(1)
        
        assert result.is_enabled == 0
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_get_task_list_all(self, mock_task_class):
        """测试获取所有任务列表"""
        mock_query = Mock()
        mock_pagination = Mock()
        mock_pagination.items = [Mock(), Mock()]
        mock_pagination.total = 2
        mock_pagination.page = 1
        mock_pagination.per_page = 10
        
        mock_task_class.query = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        
        tasks, total, page, page_size = self.service.get_task_list(page=1, page_size=10)
        
        assert len(tasks) == 2
        assert total == 2
        assert page == 1
    
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_get_task_list_filtered(self, mock_task_class):
        """测试获取过滤后的任务列表"""
        mock_query = Mock()
        mock_pagination = Mock()
        mock_pagination.items = [Mock()]
        mock_pagination.total = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 10
        
        mock_task_class.query = mock_query
        filtered_query = Mock()
        mock_query.filter_by.return_value = filtered_query
        filtered_query.order_by.return_value = filtered_query
        filtered_query.paginate.return_value = mock_pagination
        
        tasks, total, page, page_size = self.service.get_task_list(
            page=1, 
            page_size=10,
            is_enabled=1
        )
        
        mock_query.filter_by.assert_called_once_with(is_enabled=1)
        assert len(tasks) == 1
    
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_get_task_detail(self, mock_task_class):
        """测试获取任务详情"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        
        result = self.service.get_task_detail(1)
        
        assert result == mock_task
    
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_get_task_detail_not_found(self, mock_task_class):
        """测试获取任务详情不存在"""
        mock_task_class.query.get.return_value = None
        
        with pytest.raises(ValueError, match="Task not found"):
            self.service.get_task_detail(999)
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    @patch('app.services.sql_export_service.SqlExportLog')
    @patch('app.services.sql_export_service.execute_sql')
    @patch('app.services.sql_export_service.export_to_excel')
    def test_execute_task_success(
        self, 
        mock_export_excel, 
        mock_execute_sql, 
        mock_log_class, 
        mock_task_class,
        mock_db
    ):
        """测试执行任务成功"""
        # Mock task
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.task_name = '测试任务'
        mock_task.datasource_type = 'mysql'
        mock_task.get_datasource_config.return_value = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': 'encrypted',
            'database': 'test_db'
        }
        mock_task.get_time_params.return_value = {}
        mock_task.sql_template = 'SELECT * FROM test_table'
        mock_task.export_path = './exports/'
        mock_task.filename_prefix = 'export'
        mock_task.batch_size = 5000
        mock_task_class.query.get.return_value = mock_task
        
        # Mock log
        mock_log = Mock()
        mock_log.status = 'running'
        mock_log_class.return_value = mock_log
        
        # Mock SQL execution
        mock_df = pd.DataFrame({'id': [1, 2, 3], 'name': ['a', 'b', 'c']})
        mock_execute_sql.return_value = (mock_df, 3)
        
        # Mock Excel export
        mock_export_excel.return_value = ['./exports/export_1.xlsx']
        
        with patch('app.services.sql_export_service.calculate_all_time_params', return_value={}):
            with patch('app.services.sql_export_service.get_file_size', return_value=1024):
                result = self.service.execute_task(1)
                
                assert result['success'] is True
                assert result['record_count'] == 3
                assert len(result['file_paths']) == 1
                assert mock_log.status == 'success'
                assert mock_log.record_count == 3
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    @patch('app.services.sql_export_service.SqlExportLog')
    @patch('app.services.sql_export_service.execute_sql')
    def test_execute_task_no_data(
        self,
        mock_execute_sql,
        mock_log_class,
        mock_task_class,
        mock_db
    ):
        """测试执行任务无数据"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.get_datasource_config.return_value = {}
        mock_task.get_time_params.return_value = {}
        mock_task.sql_template = 'SELECT * FROM empty_table'
        mock_task_class.query.get.return_value = mock_task
        
        mock_log = Mock()
        mock_log_class.return_value = mock_log
        
        mock_df = pd.DataFrame()
        mock_execute_sql.return_value = (mock_df, 0)
        
        with patch('app.services.sql_export_service.calculate_all_time_params', return_value={}):
            result = self.service.execute_task(1)
            
            assert result['success'] is True
            assert result['record_count'] == 0
            assert result['file_paths'] == []
            assert mock_log.status == 'success'
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    @patch('app.services.sql_export_service.SqlExportLog')
    @patch('app.services.sql_export_service.execute_sql')
    def test_execute_task_failed(
        self,
        mock_execute_sql,
        mock_log_class,
        mock_task_class,
        mock_db
    ):
        """测试执行任务失败"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.get_datasource_config.return_value = {}
        mock_task.get_time_params.return_value = {}
        mock_task.sql_template = 'SELECT * FROM test_table'
        mock_task_class.query.get.return_value = mock_task
        
        mock_log = Mock()
        mock_log_class.return_value = mock_log
        
        mock_execute_sql.side_effect = Exception("SQL执行失败")
        
        with patch('app.services.sql_export_service.calculate_all_time_params', return_value={}):
            with pytest.raises(Exception, match="SQL执行失败"):
                self.service.execute_task(1)
            
            assert mock_log.status == 'failed'
            assert mock_log.error_message == "SQL执行失败"
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    def test_execute_task_not_found(self, mock_task_class, mock_db):
        """测试执行任务不存在"""
        mock_task_class.query.get.return_value = None
        
        with pytest.raises(ValueError, match="Task not found"):
            self.service.execute_task(999)
    
    @patch('app.services.sql_export_service.SqlExportLog')
    def test_get_execution_logs_all(self, mock_log_class):
        """测试获取所有执行日志"""
        mock_query = Mock()
        mock_pagination = Mock()
        mock_pagination.items = [Mock(), Mock()]
        mock_pagination.total = 2
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        
        mock_log_class.query = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.paginate.return_value = mock_pagination
        
        logs, total, page, page_size = self.service.get_execution_logs(page=1, page_size=20)
        
        assert len(logs) == 2
        assert total == 2
    
    @patch('app.services.sql_export_service.SqlExportLog')
    def test_get_execution_logs_by_task(self, mock_log_class):
        """测试获取指定任务的执行日志"""
        mock_query = Mock()
        mock_pagination = Mock()
        mock_pagination.items = [Mock()]
        mock_pagination.total = 1
        
        mock_log_class.query = mock_query
        filtered_query = Mock()
        mock_query.filter_by.return_value = filtered_query
        filtered_query.order_by.return_value = filtered_query
        filtered_query.paginate.return_value = mock_pagination
        
        logs, total, page, page_size = self.service.get_execution_logs(
            task_id=1,
            page=1,
            page_size=20
        )
        
        mock_query.filter_by.assert_called_once_with(task_id=1)
        assert len(logs) == 1
    
    @patch('app.services.sql_export_service.db')
    @patch('app.services.sql_export_service.SqlExportTask')
    @patch('app.services.sql_export_service.SqlExportLog')
    @patch('app.services.sql_export_service.execute_sql')
    @patch('app.services.sql_export_service.export_to_excel')
    def test_execute_task_with_override_params(
        self,
        mock_export_excel,
        mock_execute_sql,
        mock_log_class,
        mock_task_class,
        mock_db
    ):
        """测试使用覆盖参数执行任务"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task.get_datasource_config.return_value = {}
        mock_task.get_time_params.return_value = {}
        mock_task.sql_template = 'SELECT * FROM test_table'
        mock_task.export_path = './exports/'
        mock_task.filename_prefix = 'export'
        mock_task.batch_size = 5000
        mock_task_class.query.get.return_value = mock_task
        
        mock_log = Mock()
        mock_log_class.return_value = mock_log
        
        mock_df = pd.DataFrame({'id': [1]})
        mock_execute_sql.return_value = (mock_df, 1)
        mock_export_excel.return_value = ['./exports/export_1.xlsx']
        
        override_params = {
            'start_time': '2024-01-01 00:00:00',
            'end_time': '2024-01-02 00:00:00'
        }
        
        with patch('app.services.sql_export_service.calculate_all_time_params', return_value={}):
            with patch('app.services.sql_export_service.get_file_size', return_value=100):
                result = self.service.execute_task(1, override_time_params=override_params)
                
                assert result['success'] is True
                # 验证使用了覆盖参数而非计算参数
