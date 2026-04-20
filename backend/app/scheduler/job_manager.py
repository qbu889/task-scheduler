"""
定时任务调度器
集成APScheduler，支持动态管理SQL导出任务
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.sql_export_service import sql_export_service
from app.models.sql_export_task import SqlExportTask
import logging
import atexit

logger = logging.getLogger(__name__)


class JobManager:
    """定时任务管理器"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.app = None
    
    def init_app(self, app):
        """
        初始化应用
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        
        # 启动调度器
        self.scheduler.start()
        
        # 加载所有已启用的任务
        self.load_all_tasks()
        
        # 应用退出时关闭调度器
        atexit.register(lambda: self.shutdown())
        
        logger.info("JobManager initialized")
    
    def load_all_tasks(self):
        """加载所有已启用的SQL导出任务"""
        with self.app.app_context():
            try:
                logger.info("Loading all enabled scheduled tasks")
                
                tasks = SqlExportTask.query.filter_by(is_enabled=1).all()
                
                for task in tasks:
                    self.add_job(task.task_id, task.cron_expression, task.task_name)
                
                logger.info(f"Successfully loaded {len(tasks)} scheduled tasks")
                
            except Exception as e:
                logger.error(f"Failed to load tasks: {str(e)}", exc_info=True)
    
    def add_job(self, task_id, cron_expression, task_name=None):
        """
        添加定时任务
        
        Args:
            task_id (int): 任务ID
            cron_expression (str): Cron表达式
            task_name (str): 任务名称（用于日志）
        """
        try:
            job_id = f"sql_export_{task_id}"
            
            # 如果任务已存在，先移除
            if self.scheduler.get_job(job_id):
                logger.debug(f"Removing existing job: {job_id}")
                self.scheduler.remove_job(job_id)
            
            # 创建Cron触发器
            trigger = CronTrigger.from_crontab(cron_expression)
            
            # 添加任务
            self.scheduler.add_job(
                func=self._execute_export_task,
                trigger=trigger,
                id=job_id,
                args=[task_id],
                replace_existing=True,
                name=f"SQL Export: {task_name or task_id}"
            )
            
            logger.info(f"Job added successfully: job_id={job_id}, task_name={task_name}, cron={cron_expression}")
            
        except Exception as e:
            logger.error(f"Failed to add job for task {task_id}: {str(e)}", exc_info=True)
            raise
    
    def remove_job(self, task_id):
        """
        移除定时任务
        
        Args:
            task_id (int): 任务ID
        """
        job_id = f"sql_export_{task_id}"
        
        try:
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Job removed successfully: job_id={job_id}")
            else:
                logger.debug(f"Job not found for removal: job_id={job_id}")
            
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}", exc_info=True)
    
    def update_job(self, task_id, cron_expression):
        """
        更新定时任务的Cron表达式
        
        Args:
            task_id (int): 任务ID
            cron_expression (str): 新的Cron表达式
        """
        self.remove_job(task_id)
        self.add_job(task_id, cron_expression)
    
    def _execute_export_task(self, task_id):
        """
        执行导出任务（调度器回调）
        
        Args:
            task_id (int): 任务ID
        """
        import time
        start_time = time.time()
        
        with self.app.app_context():
            try:
                logger.info(f"Executing scheduled export task: task_id={task_id}")
                
                result = sql_export_service.execute_task(task_id)
                
                duration = time.time() - start_time
                logger.info(f"Scheduled task completed successfully: task_id={task_id}, "
                          f"rows={result.get('record_count', 0)}, duration={duration:.2f}s")
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Scheduled task failed: task_id={task_id}, duration={duration:.2f}s, error={str(e)}", 
                           exc_info=True)
    
    def shutdown(self):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")


# 创建全局实例
job_manager = JobManager()
