"""
文件清理API单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json


class TestCleanupAPI:
    """文件清理API测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        from app import create_app
        from tests.config.testing import TestingConfig
        
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_files_success(self, mock_cleanup_service):
        """测试手动触发文件清理成功"""
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 150,
            'total_deleted': 45,
            'total_size_freed': 524288000,  # 500MB
            'errors': [],
            'paths_cleaned': {}
        }
        
        response = self.client.post('/api/cleanup/files')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['total_scanned'] == 150
        assert data['data']['total_deleted'] == 45
        assert data['data']['total_size_freed_mb'] == 500.0
        
        mock_cleanup_service.clean_old_files.assert_called_once_with(7)
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_files_custom_retention(self, mock_cleanup_service):
        """测试使用自定义保留天数清理"""
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 100,
            'total_deleted': 30,
            'total_size_freed': 104857600,  # 100MB
            'errors': []
        }
        
        response = self.client.post('/api/cleanup/files?retention_days=30')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['total_deleted'] == 30
        
        mock_cleanup_service.clean_old_files.assert_called_once_with(30)
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_files_exception(self, mock_cleanup_service):
        """测试清理文件异常"""
        mock_cleanup_service.clean_old_files.side_effect = Exception("Cleanup failed")
        
        response = self.client.post('/api/cleanup/files')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert data['success'] is False
        assert 'Cleanup failed' in data['message']
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_get_cleanup_report_success(self, mock_cleanup_service):
        """测试获取清理报告成功"""
        mock_cleanup_service.get_cleanup_report.return_value = {
            'retention_days': 7,
            'total_scanned': 150,
            'files_to_delete': [
                {
                    'file_path': '/exports/test_20260413_020000.xlsx',
                    'filename': 'test_20260413_020000.xlsx',
                    'file_size': 10485760,
                    'file_age_days': 7,
                    'timestamp': '2026-04-13T02:00:00'
                }
            ],
            'total_size_to_free': 10485760,
            'errors': []
        }
        
        response = self.client.get('/api/cleanup/files/report')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['retention_days'] == 7
        assert len(data['data']['files_to_delete']) == 1
        assert data['data']['total_size_to_free_mb'] == 10.0
        
        mock_cleanup_service.get_cleanup_report.assert_called_once_with(7)
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_get_cleanup_report_custom_retention(self, mock_cleanup_service):
        """测试获取自定义保留天数的清理报告"""
        mock_cleanup_service.get_cleanup_report.return_value = {
            'retention_days': 30,
            'total_scanned': 100,
            'files_to_delete': [],
            'total_size_to_free': 0,
            'errors': []
        }
        
        response = self.client.get('/api/cleanup/files/report?retention_days=30')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['retention_days'] == 30
        assert len(data['data']['files_to_delete']) == 0
        
        mock_cleanup_service.get_cleanup_report.assert_called_once_with(30)
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_get_cleanup_report_exception(self, mock_cleanup_service):
        """测试获取清理报告异常"""
        mock_cleanup_service.get_cleanup_report.side_effect = Exception("Report generation failed")
        
        response = self.client.get('/api/cleanup/files/report')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert data['success'] is False
        assert 'Report generation failed' in data['message']
    
    @patch('app.models.sql_export_task.SqlExportTask')
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_task_files_success(self, mock_cleanup_service, mock_task_class):
        """测试清理指定任务的文件成功"""
        # Mock task
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        
        mock_cleanup_service.cleanup_by_task_id.return_value = {
            'total_scanned': 50,
            'total_deleted': 10,
            'total_size_freed': 52428800,  # 50MB
            'errors': []
        }
        
        response = self.client.post('/api/cleanup/files/task/1')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert data['data']['total_scanned'] == 50
        assert data['data']['total_deleted'] == 10
        assert data['data']['total_size_freed_mb'] == 50.0
        
        mock_cleanup_service.cleanup_by_task_id.assert_called_once_with(1, 7)
    
    @patch('app.models.sql_export_task.SqlExportTask')
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_task_files_custom_retention(self, mock_cleanup_service, mock_task_class):
        """测试使用自定义保留天数清理指定任务"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        
        mock_cleanup_service.cleanup_by_task_id.return_value = {
            'total_scanned': 30,
            'total_deleted': 5,
            'total_size_freed': 10485760,
            'errors': []
        }
        
        response = self.client.post('/api/cleanup/files/task/1?retention_days=14')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        
        mock_cleanup_service.cleanup_by_task_id.assert_called_once_with(1, 14)
    
    @patch('app.models.sql_export_task.SqlExportTask')
    def test_cleanup_task_files_not_found(self, mock_task_class):
        """测试清理不存在的任务文件"""
        mock_task_class.query.get.return_value = None
        
        response = self.client.post('/api/cleanup/files/task/999')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert data['success'] is False
        assert 'Task not found' in data['message']
    
    @patch('app.models.sql_export_task.SqlExportTask')
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_task_files_exception(self, mock_cleanup_service, mock_task_class):
        """测试清理任务文件异常"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        
        mock_cleanup_service.cleanup_by_task_id.side_effect = ValueError("Invalid retention days")
        
        response = self.client.post('/api/cleanup/files/task/1')
        data = json.loads(response.data)
        
        assert response.status_code == 400
        assert data['success'] is False
        assert 'Invalid retention days' in data['message']
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_files_invalid_retention_days(self, mock_cleanup_service):
        """测试无效的保留天数参数"""
        response = self.client.post('/api/cleanup/files?retention_days=-5')
        data = json.loads(response.data)
        
        # Flask应该会自动处理无效的参数类型
        # 如果传入负数，可能会被转换为默认值或返回错误
        assert response.status_code in [200, 400]
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_files_zero_retention_days(self, mock_cleanup_service):
        """测试保留天数为0（删除所有文件）"""
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 100,
            'total_deleted': 100,
            'total_size_freed': 1048576000,
            'errors': []
        }
        
        response = self.client.post('/api/cleanup/files?retention_days=0')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        # 保留0天应该删除所有文件
        assert data['data']['total_deleted'] == 100
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_report_empty_result(self, mock_cleanup_service):
        """测试清理报告无待删除文件"""
        mock_cleanup_service.get_cleanup_report.return_value = {
            'retention_days': 7,
            'total_scanned': 50,
            'files_to_delete': [],
            'total_size_to_free': 0,
            'errors': []
        }
        
        response = self.client.get('/api/cleanup/files/report')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']['files_to_delete']) == 0
        assert data['data']['total_size_to_free_mb'] == 0.0
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_report_large_dataset(self, mock_cleanup_service):
        """测试清理报告大数据集"""
        # 模拟大量待删除文件
        files_to_delete = [
            {
                'file_path': f'/exports/file_{i}_20260413_020000.xlsx',
                'filename': f'file_{i}_20260413_020000.xlsx',
                'file_size': 1048576,  # 1MB
                'file_age_days': 10,
                'timestamp': '2026-04-13T02:00:00'
            }
            for i in range(100)
        ]
        
        mock_cleanup_service.get_cleanup_report.return_value = {
            'retention_days': 7,
            'total_scanned': 500,
            'files_to_delete': files_to_delete,
            'total_size_to_free': 104857600,  # 100MB
            'errors': []
        }
        
        response = self.client.get('/api/cleanup/files/report')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['success'] is True
        assert len(data['data']['files_to_delete']) == 100
        assert data['data']['total_size_to_free_mb'] == 100.0
    
    @patch('app.models.sql_export_task.SqlExportTask')
    @patch('app.api.cleanup.file_cleanup_service')
    def test_cleanup_task_with_errors(self, mock_cleanup_service, mock_task_class):
        """测试清理任务有错误"""
        mock_task = Mock()
        mock_task.task_id = 1
        mock_task_class.query.get.return_value = mock_task
        mock_cleanup_service.cleanup_by_task_id.return_value = {
            'total_scanned': 50,
            'total_deleted': 45,
            'total_size_freed': 47185920,
            'errors': ['Failed to delete file1', 'Failed to delete file2']
        }

        response = self.client.post('/api/cleanup/files/task/1')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        # 即使有错误，也应该返回成功的统计信息


class TestCleanupAPIIntegration:
    """文件清理API集成测试"""
    
    def setup_method(self):
        """设置测试环境"""
        from app import create_app
        from tests.config.testing import TestingConfig
        
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_full_cleanup_workflow(self, mock_cleanup_service):
        """测试完整的清理工作流程"""
        # 1. 先获取清理报告
        mock_cleanup_service.get_cleanup_report.return_value = {
            'retention_days': 7,
            'total_scanned': 100,
            'files_to_delete': [
                {
                    'file_path': '/exports/test_20260413_020000.xlsx',
                    'filename': 'test_20260413_020000.xlsx',
                    'file_size': 10485760,
                    'file_age_days': 7,
                    'timestamp': '2026-04-13T02:00:00'
                }
            ],
            'total_size_to_free': 10485760,
            'errors': []
        }
        
        report_response = self.client.get('/api/cleanup/files/report')
        report_data = json.loads(report_response.data)
        
        assert report_response.status_code == 200
        assert len(report_data['data']['files_to_delete']) > 0
        
        # 2. 执行清理
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 100,
            'total_deleted': 1,
            'total_size_freed': 10485760,
            'errors': []
        }
        
        cleanup_response = self.client.post('/api/cleanup/files')
        cleanup_data = json.loads(cleanup_response.data)
        
        assert cleanup_response.status_code == 200
        assert cleanup_data['data']['total_deleted'] == 1
        
        # 3. 验证清理结果
        assert cleanup_data['data']['total_size_freed_mb'] == 10.0
    
    @patch('app.api.cleanup.file_cleanup_service')
    def test_multiple_cleanup_operations(self, mock_cleanup_service):
        """测试多次清理操作"""
        # 第一次清理
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 100,
            'total_deleted': 20,
            'total_size_freed': 209715200,
            'errors': []
        }
        
        response1 = self.client.post('/api/cleanup/files')
        data1 = json.loads(response1.data)
        
        assert response1.status_code == 200
        assert data1['data']['total_deleted'] == 20
        
        # 第二次清理（可能没有更多文件需要清理）
        mock_cleanup_service.clean_old_files.return_value = {
            'total_scanned': 80,
            'total_deleted': 0,
            'total_size_freed': 0,
            'errors': []
        }
        
        response2 = self.client.post('/api/cleanup/files')
        data2 = json.loads(response2.data)
        
        assert response2.status_code == 200
        assert data2['data']['total_deleted'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
