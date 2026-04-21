import os
from datetime import timedelta


class BaseConfig:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # 加密密钥（用于数据源密码加密）
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-change-me')
    
    # 导出配置
    EXPORT_DEFAULT_PATH = os.getenv('EXPORT_DEFAULT_PATH', './exports/')
    EXPORT_MAX_ROWS_PER_FILE = 50000
    
    # 邮件配置
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_RECEIVER = '524722511@qq.com'


class DevelopmentConfig(BaseConfig):
    """开发环境配置 - MySQL"""
    DEBUG = True
    
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345678')
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'task_scheduler_dev')
    
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@'
        f'{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    )


class ProductionConfig(BaseConfig):
    """生产环境配置 - 达梦数据库"""
    DEBUG = False
    
    DM_USER = os.getenv('DM_USER', 'SYSDBA')
    DM_PASSWORD = os.getenv('DM_PASSWORD', '')
    DM_HOST = os.getenv('DM_HOST', '127.0.0.1')
    DM_PORT = os.getenv('DM_PORT', '5236')
    DM_DATABASE = os.getenv('DM_DATABASE', 'TASK_DB')
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # 延迟检查达梦驱动是否已安装
        try:
            import dmPython
            import sqlalchemy_dm
            return (
                f'dm+dmPython://{self.DM_USER}:{self.DM_PASSWORD}@'
                f'{self.DM_HOST}:{self.DM_PORT}/{self.DM_DATABASE}?charset=utf8'
            )
        except ImportError:
            raise ImportError(
                "生产环境需要达梦数据库驱动，请手动安装:\n"
                "1. 从达梦数据库安装包的 drivers/python 目录获取 dmPython 和 sqlalchemy_dm 源码\n"
                "2. 编译安装: cd dmPython && python setup.py install\n"
                "3. 编译安装: cd sqlalchemy_dm && python setup.py install\n"
                "详细步骤请参考达梦官方文档"
            )
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 30,
            'autoCommit': False
        }
    }


# 配置映射
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 从环境变量获取当前环境
current_env = os.getenv('FLASK_ENV', 'development')
Config = config_map.get(current_env, config_map['default'])
