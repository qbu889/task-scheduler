"""
SQL导出API集成测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestSqlExportApi:
    """SQL导出API测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from app import create_app
        
        app = create_app('tests.config.testing.TestingConfig')
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.test_client() as client:
            with app.app_context():
                yield client
    
    def test_get_tasks_list(self, client):
        """测试获取任务列表"""
        with patch('app.api.sql_export.sql_export_service.get_task_list') as mock_get:
            mock_task = Mock()
            mock_task.to_dict.return_value = {'task_id': 1, 'task_name': '测试任务'}
            mock_get.return_value = ([mock_task], 1, 1, 10)
            
            response = client.get('/api/sql-export/tasks?page=1&page_size=10')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 1
    
    def test_get_tasks_with_filter(self, client):
        """测试获取过滤后的任务列表"""
        with patch('app.api.sql_export.sql_export_service.get_task_list') as mock_get:
            mock_get.return_value = ([], 0, 1, 10)
            
            response = client.get('/api/sql-export/tasks?is_enabled=1')
            
            assert response.status_code == 200
            mock_get.assert_called_once_with(page=1, page_size=10, is_enabled=1)
    
    def test_get_tasks_error(self, client):
        """测试获取任务列表异常"""
        with patch('app.api.sql_export.sql_export_service.get_task_list') as mock_get:
            mock_get.side_effect = Exception("Database error")
            
            response = client.get('/api/sql-export/tasks')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_get_task_detail(self, client):
        """测试获取任务详情"""
        with patch('app.api.sql_export.sql_export_service.get_task_detail') as mock_get:
            mock_task = Mock()
            mock_task.to_dict.return_value = {'task_id': 1, 'task_name': '测试任务'}
            mock_get.return_value = mock_task
            
            response = client.get('/api/sql-export/tasks/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['task_id'] == 1
    
    def test_get_task_not_found(self, client):
        """测试获取不存在的任务"""
        with patch('app.api.sql_export.sql_export_service.get_task_detail') as mock_get:
            mock_get.side_effect = ValueError("Task not found: 999")
            
            response = client.get('/api/sql-export/tasks/999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_create_task_success(self, client):
        """测试创建任务成功"""
        with patch('app.api.sql_export.sql_export_service.create_task') as mock_create:
            mock_task = Mock()
            mock_task.to_dict.return_value = {
                'task_id': 1,
                'task_name': '新任务'
            }
            mock_create.return_value = mock_task
            
            task_data = {
                'task_name': '新任务',
                'datasource_type': 'mysql',
                'datasource_config': {
                    'host': '127.0.0.1',
                    'port': 3306,
                    'user': 'root',
                    'password': '12345678',
                    'database': 'test_db'
                },
                'sql_template': 'SELECT * FROM test_table',
                'time_params': {},
                'cron_expression': '0 0 2 * * *'
            }
            
            response = client.post(
                '/api/sql-export/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == 'Task created successfully'
    
    def test_create_task_missing_field(self, client):
        """测试创建任务缺少必填字段"""
        task_data = {
            'task_name': '新任务',
            # 缺少其他必填字段
        }
        
        response = client.post(
            '/api/sql-export/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Missing required field' in data['message']
    
    def test_update_task_success(self, client):
        """测试更新任务成功"""
        with patch('app.api.sql_export.sql_export_service.update_task') as mock_update:
            mock_task = Mock()
            mock_task.to_dict.return_value = {'task_id': 1, 'task_name': '更新后的任务'}
            mock_update.return_value = mock_task
            
            update_data = {
                'task_name': '更新后的任务',
                'cron_expression': '0 0 3 * * *'
            }
            
            response = client.put(
                '/api/sql-export/tasks/1',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_update_task_not_found(self, client):
        """测试更新不存在的任务"""
        with patch('app.api.sql_export.sql_export_service.update_task') as mock_update:
            mock_update.side_effect = ValueError("Task not found: 999")
            
            response = client.put(
                '/api/sql-export/tasks/999',
                data=json.dumps({}),
                content_type='application/json'
            )
            
            assert response.status_code == 404
    
    def test_delete_task_success(self, client):
        """测试删除任务成功"""
        with patch('app.api.sql_export.sql_export_service.delete_task') as mock_delete:
            mock_delete.return_value = None
            
            response = client.delete('/api/sql-export/tasks/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == 'Task deleted successfully'
    
    def test_delete_task_not_found(self, client):
        """测试删除不存在的任务"""
        with patch('app.api.sql_export.sql_export_service.delete_task') as mock_delete:
            mock_delete.side_effect = ValueError("Task not found: 999")
            
            response = client.delete('/api/sql-export/tasks/999')
            
            assert response.status_code == 404
    
    def test_enable_task(self, client):
        """测试启用任务"""
        with patch('app.api.sql_export.sql_export_service.enable_task') as mock_enable:
            mock_task = Mock()
            mock_task.to_dict.return_value = {'task_id': 1, 'is_enabled': 1}
            mock_enable.return_value = mock_task
            
            response = client.put('/api/sql-export/tasks/1/enable')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == 'Task enabled'
    
    def test_disable_task(self, client):
        """测试停用任务"""
        with patch('app.api.sql_export.sql_export_service.disable_task') as mock_disable:
            mock_task = Mock()
            mock_task.to_dict.return_value = {'task_id': 1, 'is_enabled': 0}
            mock_disable.return_value = mock_task
            
            response = client.put('/api/sql-export/tasks/1/disable')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == 'Task disabled'
    
    def test_trigger_task_success(self, client):
        """测试手动触发任务执行成功"""
        with patch('app.api.sql_export.sql_export_service.execute_task') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'message': '导出成功',
                'record_count': 100,
                'file_paths': ['./exports/export_1.xlsx']
            }
            
            response = client.post('/api/sql-export/tasks/1/trigger')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['record_count'] == 100
    
    def test_trigger_task_with_override_params(self, client):
        """测试使用覆盖参数触发任务"""
        with patch('app.api.sql_export.sql_export_service.execute_task') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'message': '导出成功',
                'record_count': 50,
                'file_paths': []
            }
            
            override_data = {
                'override_time_params': {
                    'start_time': '2024-01-01 00:00:00',
                    'end_time': '2024-01-02 00:00:00'
                }
            }
            
            response = client.post(
                '/api/sql-export/tasks/1/trigger',
                data=json.dumps(override_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            mock_execute.assert_called_once_with(
                1, 
                override_data['override_time_params']
            )
    
    def test_trigger_task_not_found(self, client):
        """测试触发不存在的任务"""
        with patch('app.api.sql_export.sql_export_service.execute_task') as mock_execute:
            mock_execute.side_effect = ValueError("Task not found: 999")
            
            response = client.post('/api/sql-export/tasks/999/trigger')
            
            assert response.status_code == 404
    
    def test_trigger_task_execution_error(self, client):
        """测试任务执行失败"""
        with patch('app.api.sql_export.sql_export_service.execute_task') as mock_execute:
            mock_execute.side_effect = Exception("Execution failed")
            
            response = client.post('/api/sql-export/tasks/1/trigger')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_get_logs_list(self, client):
        """测试获取执行日志列表"""
        with patch('app.api.sql_export.sql_export_service.get_execution_logs') as mock_get:
            mock_log = Mock()
            mock_log.to_dict.return_value = {
                'log_id': 1,
                'task_id': 1,
                'status': 'success'
            }
            mock_get.return_value = ([mock_log], 1, 1, 20)
            
            response = client.get('/api/sql-export/logs?page=1&page_size=20')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']) == 1
    
    def test_get_logs_by_task(self, client):
        """测试获取指定任务的执行日志"""
        with patch('app.api.sql_export.sql_export_service.get_execution_logs') as mock_get:
            mock_get.return_value = ([], 0, 1, 20)
            
            response = client.get('/api/sql-export/logs?task_id=1')
            
            assert response.status_code == 200
            mock_get.assert_called_once_with(task_id=1, page=1, page_size=20)
    
    def test_get_log_detail(self, client):
        """测试获取日志详情"""
        from app.models.sql_export_log import SqlExportLog
        
        with patch.object(SqlExportLog.query, 'get') as mock_get:
            mock_log = Mock()
            mock_log.to_dict.return_value = {
                'log_id': 1,
                'task_id': 1,
                'status': 'success',
                'record_count': 100
            }
            mock_get.return_value = mock_log
            
            response = client.get('/api/sql-export/logs/1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['log_id'] == 1
    
    def test_get_log_detail_not_found(self, client):
        """测试获取不存在的日志"""
        from app.models.sql_export_log import SqlExportLog
        
        with patch.object(SqlExportLog.query, 'get') as mock_get:
            mock_get.return_value = None
            
            response = client.get('/api/sql-export/logs/999')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_create_task_error_handling(self, client):
        """测试创建任务异常处理"""
        with patch('app.api.sql_export.sql_export_service.create_task') as mock_create:
            mock_create.side_effect = Exception("Unexpected error")
            
            task_data = {
                'task_name': '新任务',
                'datasource_type': 'mysql',
                'datasource_config': {},
                'sql_template': 'SELECT * FROM test',
                'time_params': {},
                'cron_expression': '0 0 2 * * *'
            }
            
            response = client.post(
                '/api/sql-export/tasks',
                data=json.dumps(task_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_update_task_error_handling(self, client):
        """测试更新任务异常处理"""
        with patch('app.api.sql_export.sql_export_service.update_task') as mock_update:
            mock_update.side_effect = Exception("Update error")
            
            response = client.put(
                '/api/sql-export/tasks/1',
                data=json.dumps({'task_name': 'New Name'}),
                content_type='application/json'
            )
            
            assert response.status_code == 500
    
    def test_delete_task_error_handling(self, client):
        """测试删除任务异常处理"""
        with patch('app.api.sql_export.sql_export_service.delete_task') as mock_delete:
            mock_delete.side_effect = Exception("Delete error")
            
            response = client.delete('/api/sql-export/tasks/1')
            
            assert response.status_code == 500
    
    def test_enable_task_error_handling(self, client):
        """测试启用任务异常处理"""
        with patch('app.api.sql_export.sql_export_service.enable_task') as mock_enable:
            mock_enable.side_effect = Exception("Enable error")
            
            response = client.put('/api/sql-export/tasks/1/enable')
            
            assert response.status_code == 500
    
    def test_disable_task_error_handling(self, client):
        """测试停用任务异常处理"""
        with patch('app.api.sql_export.sql_export_service.disable_task') as mock_disable:
            mock_disable.side_effect = Exception("Disable error")
            
            response = client.put('/api/sql-export/tasks/1/disable')
            
            assert response.status_code == 500
    
    def test_get_logs_error_handling(self, client):
        """测试获取日志异常处理"""
        with patch('app.api.sql_export.sql_export_service.get_execution_logs') as mock_get:
            mock_get.side_effect = Exception("Query error")
            
            response = client.get('/api/sql-export/logs')
            
            assert response.status_code == 500
