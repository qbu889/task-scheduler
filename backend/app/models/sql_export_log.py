"""
SQL导出执行日志数据模型
"""
from app import db
from datetime import datetime


class SqlExportLog(db.Model):
    """SQL导出执行日志表"""
    __tablename__ = 'sql_export_log'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='日志ID')
    task_id = db.Column(db.Integer, db.ForeignKey('sql_export_task.task_id'), nullable=False, comment='任务ID')
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    status = db.Column(db.String(20), nullable=False, comment='执行状态：success/failed')
    record_count = db.Column(db.Integer, default=0, comment='记录数')
    file_path = db.Column(db.String(500), comment='文件路径')
    file_size = db.Column(db.BigInteger, comment='文件大小（字节）')
    duration_seconds = db.Column(db.Float, comment='耗时（秒）')
    error_message = db.Column(db.Text, comment='错误信息')
    final_sql = db.Column(db.Text, comment='实际执行的完整SQL')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 日志信息字典
        """
        return {
            'log_id': self.log_id,
            'task_id': self.task_id,
            'task_name': self.task.task_name if self.task else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'record_count': self.record_count,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration_seconds': self.duration_seconds,
            'final_sql': self.final_sql,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SqlExportLog {self.log_id} - {self.status}>'
