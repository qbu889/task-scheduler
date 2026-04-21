"""
task-scheduler Flask应用工厂
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
import logging
import os
from logging.handlers import RotatingFileHandler

# 初始化扩展
db = SQLAlchemy()


def setup_logging(app):
    """
    配置日志系统
    
    Args:
        app: Flask应用实例
    """
    # 获取日志配置
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    log_format = app.config.get('LOG_FORMAT', 
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    log_file = app.config.get('LOG_FILE', 'app.log')
    max_bytes = app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024)  # 10MB
    backup_count = app.config.get('LOG_BACKUP_COUNT', 5)
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # 配置Flask日志
    app.logger.handlers = []
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)
    
    app.logger.info(f"Logging system initialized: level={logging.getLevelName(log_level)}, file={log_file}")


def create_app(config_class=None):
    """
    创建Flask应用
    
    Args:
        config_class: 配置类，默认使用config.py中的Config
        
    Returns:
        Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置JSON序列化：确保中文原样输出，不使用Unicode转义
    app.json.ensure_ascii = False
    
    # 加载配置
    if config_class is None:
        from config import Config as AppConfig
        app.config.from_object(AppConfig)
    else:
        app.config.from_object(config_class)
    
    # 配置日志系统
    setup_logging(app)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})
    
    # 注册蓝图
    register_blueprints(app)
    
    # 初始化调度器
    init_scheduler(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    
    app.logger.info("Application created successfully")
    return app


def register_blueprints(app):
    """注册API蓝图"""
    from app.api.sql_export import sql_export_bp
    from app.api.cleanup import cleanup_bp
    
    app.register_blueprint(sql_export_bp, url_prefix='/api/sql-export')
    app.register_blueprint(cleanup_bp, url_prefix='/api/cleanup')


def init_scheduler(app):
    """初始化定时任务调度器"""
    # 在debug模式下，只在主进程中初始化调度器（避免reloader导致重复初始化）
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.scheduler.job_manager import job_manager
        job_manager.init_app(app)
    else:
        app.logger.debug("Skipping scheduler initialization in reloader process")
