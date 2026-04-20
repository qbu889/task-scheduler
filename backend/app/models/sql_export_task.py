"""
SQL导出任务数据模型
"""
from app import db
from datetime import datetime
import json


class SqlExportTask(db.Model):
    """SQL导出任务配置表"""
    __tablename__ = 'sql_export_task'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='任务ID')
    task_name = db.Column(db.String(200), nullable=False, comment='任务名称')
    datasource_type = db.Column(db.String(50), nullable=False, comment='数据源类型：mysql/dm')
    datasource_config = db.Column(db.Text, nullable=False, comment='数据源配置JSON（密码已加密）')
    sql_template = db.Column(db.Text, nullable=False, comment='SQL模板')
    time_params = db.Column(db.Text, nullable=False, comment='时间参数配置JSON')
    cron_expression = db.Column(db.String(100), nullable=False, comment='Cron表达式')
    export_path = db.Column(db.String(500), nullable=False, comment='导出路径')
    filename_prefix = db.Column(db.String(100), nullable=False, comment='文件名前缀')
    max_rows = db.Column(db.Integer, default=100000, comment='最大记录数')
    batch_size = db.Column(db.Integer, default=5000, comment='分页大小')
    is_enabled = db.Column(db.SmallInteger, default=1, comment='是否启用：0-停用 1-启用')
    description = db.Column(db.Text, comment='任务描述')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    logs = db.relationship('SqlExportLog', backref='task', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_datasource_config(self):
        """
        解密并返回数据源配置
        
        Returns:
            dict: 解密后的数据源配置
        """
        from app.utils.crypto import decrypt
        config = json.loads(self.datasource_config)
        if 'password' in config and config['password']:
            config['password'] = decrypt(config['password'])
        return config
    
    def get_time_params(self):
        """
        返回时间参数配置
        
        Returns:
            dict: 时间参数配置
        """
        return json.loads(self.time_params)
    
    def to_dict(self):
        """
        转换为字典（返回脱敏的数据源配置）
        
        Returns:
            dict: 任务信息字典
        """
        # 获取脱敏的数据源配置
        config = json.loads(self.datasource_config)
        has_password = bool(config.get('password'))
        config['password'] = '***' if has_password else ''  # 隐藏真实密码
        
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'datasource_type': self.datasource_type,
            'datasource_config': config,  # 返回脱敏后的配置
            'sql_template': self.sql_template,
            'time_params': self.get_time_params(),
            'cron_expression': self.cron_expression,
            'export_path': self.export_path,
            'filename_prefix': self.filename_prefix,
            'max_rows': self.max_rows,
            'batch_size': self.batch_size,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<SqlExportTask {self.task_name}>'
