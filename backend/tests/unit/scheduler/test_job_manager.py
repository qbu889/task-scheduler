"""
调度器单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestJobManager:
    """定时任务管理器测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        from app.scheduler.job_manager import JobManager
        self.manager = JobManager()
    
    @patch('app.scheduler.job_manager.BackgroundScheduler')
    @patch('app.scheduler.job_manager.atexit')
    def test_init_app(self, mock_atexit, mock_scheduler_class):
        """测试初始化应用"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        
        mock_app = Mock()
        
        with patch.object(self.manager, 'load_all_tasks') as mock_load:
            self.manager.init_app(mock_app)
            
            assert self.manager.app == mock_app
            mock_scheduler.start.assert_called_once()
            mock_load.assert_called_once()
            mock_atexit.register.assert_called_once()
    
    @patch('app.scheduler.job_manager.SqlExportTask')
    def test_load_all_tasks(self, mock_task_class):
        """测试加载所有任务"""
        mock_app = Mock()
        mock_context = Mock()
        mock_app.app_context.return_value.__enter__ = Mock(return_value=mock_context)
        mock_app.app_context.return_value.__exit__ = Mock(return_value=False)
        self.manager.app = mock_app
        
        # Mock tasks
        mock_task1 = Mock()
        mock_task1.task_id = 1
        mock_task1.cron_expression = '0 0 2 * * *'
        mock_task1.task_name = '任务1'
        
        mock_task2 = Mock()
        mock_task2.task_id = 2
        mock_task2.cron_expression = '0 0 3 * * *'
        mock_task2.task_name = '任务2'
        
        mock_task_class.query.filter_by.return_value.all.return_value = [mock_task1, mock_task2]
        
        with patch.object(self.manager, 'add_job') as mock_add_job:
            self.manager.load_all_tasks()
            
            assert mock_add_job.call_count == 2
            mock_add_job.assert_any_call(1, '0 0 2 * * *', '任务1')
            mock_add_job.assert_any_call(2, '0 0 3 * * *', '任务2')
    
    @patch('app.scheduler.job_manager.SqlExportTask')
    def test_load_all_tasks_empty(self, mock_task_class):
        """测试加载空任务列表"""
        mock_app = Mock()
        mock_context = Mock()
        mock_app.app_context.return_value.__enter__ = Mock(return_value=mock_context)
        mock_app.app_context.return_value.__exit__ = Mock(return_value=False)
        self.manager.app = mock_app
        
        mock_task_class.query.filter_by.return_value.all.return_value = []
        
        with patch.object(self.manager, 'add_job') as mock_add_job:
            self.manager.load_all_tasks()
            
            mock_add_job.assert_not_called()
    
    @patch('app.scheduler.job_manager.SqlExportTask')
    def test_load_all_tasks_exception(self, mock_task_class):
        """测试加载任务异常"""
        mock_app = Mock()
        mock_context = Mock()
        mock_app.app_context.return_value.__enter__ = Mock(return_value=mock_context)
        mock_app.app_context.return_value.__exit__ = Mock(return_value=False)
        self.manager.app = mock_app
        
        mock_task_class.query.filter_by.return_value.all.side_effect = Exception("DB error")
        
        # 应该捕获异常而不抛出
        self.manager.load_all_tasks()
    
    def test_add_job_new(self):
        """测试添加新任务"""
        mock_scheduler = Mock()
        mock_scheduler.get_job.return_value = None
        self.manager.scheduler = mock_scheduler
        
        self.manager.add_job(1, '0 0 2 * * *', '测试任务')
        
        mock_scheduler.add_job.assert_called_once()
        call_args = mock_scheduler.add_job.call_args
        assert call_args[1]['id'] == 'sql_export_1'
        assert call_args[1]['name'] == 'SQL Export: 测试任务'
    
    def test_add_job_replace_existing(self):
        """测试替换已存在的任务"""
        mock_scheduler = Mock()
        existing_job = Mock()
        mock_scheduler.get_job.return_value = existing_job
        self.manager.scheduler = mock_scheduler
        
        self.manager.add_job(1, '0 0 3 * * *', '更新的任务')
        
        mock_scheduler.remove_job.assert_called_once_with('sql_export_1')
        mock_scheduler.add_job.assert_called_once()
    
    def test_add_job_exception(self):
        """测试添加任务异常"""
        mock_scheduler = Mock()
        mock_scheduler.add_job.side_effect = Exception("Invalid cron")
        self.manager.scheduler = mock_scheduler
        
        with pytest.raises(Exception):
            self.manager.add_job(1, 'invalid_cron', '测试任务')
    
    def test_remove_job_exists(self):
        """测试移除存在的任务"""
        mock_scheduler = Mock()
        existing_job = Mock()
        mock_scheduler.get_job.return_value = existing_job
        self.manager.scheduler = mock_scheduler
        
        self.manager.remove_job(1)
        
        mock_scheduler.remove_job.assert_called_once_with('sql_export_1')
    
    def test_remove_job_not_exists(self):
        """测试移除不存在的任务"""
        mock_scheduler = Mock()
        mock_scheduler.get_job.return_value = None
        self.manager.scheduler = mock_scheduler
        
        self.manager.remove_job(999)
        
        mock_scheduler.remove_job.assert_not_called()
    
    def test_update_job(self):
        """测试更新任务"""
        with patch.object(self.manager, 'remove_job') as mock_remove:
            with patch.object(self.manager, 'add_job') as mock_add:
                self.manager.update_job(1, '0 0 4 * * *')
                
                mock_remove.assert_called_once_with(1)
                mock_add.assert_called_once_with(1, '0 0 4 * * *')
    
    @patch('app.scheduler.job_manager.sql_export_service')
    def test_execute_export_task_success(self, mock_service):
        """测试执行导出任务成功"""
        mock_app = Mock()
        mock_context = Mock()
        mock_app.app_context.return_value.__enter__ = Mock(return_value=mock_context)
        mock_app.app_context.return_value.__exit__ = Mock(return_value=False)
        self.manager.app = mock_app
        
        mock_service.execute_task.return_value = {
            'success': True,
            'record_count': 100
        }
        
        self.manager._execute_export_task(1)
        
        mock_service.execute_task.assert_called_once_with(1)
    
    @patch('app.scheduler.job_manager.sql_export_service')
    def test_execute_export_task_failure(self, mock_service):
        """测试执行导出任务失败"""
        mock_app = Mock()
        mock_context = Mock()
        mock_app.app_context.return_value.__enter__ = Mock(return_value=mock_context)
        mock_app.app_context.return_value.__exit__ = Mock(return_value=False)
        self.manager.app = mock_app
        
        mock_service.execute_task.side_effect = Exception("Execution failed")
        
        # 应该捕获异常而不抛出
        self.manager._execute_export_task(1)
        
        mock_service.execute_task.assert_called_once_with(1)
    
    def test_shutdown(self):
        """测试关闭调度器"""
        mock_scheduler = Mock()
        mock_scheduler.running = True
        self.manager.scheduler = mock_scheduler
        
        self.manager.shutdown()
        
        mock_scheduler.shutdown.assert_called_once()
    
    def test_shutdown_not_running(self):
        """测试关闭未运行的调度器"""
        mock_scheduler = Mock()
        mock_scheduler.running = False
        self.manager.scheduler = mock_scheduler
        
        self.manager.shutdown()
        
        mock_scheduler.shutdown.assert_not_called()
