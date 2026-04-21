"""
测试环境配置
"""
import os


class TestingConfig:
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    
    # 使用SQLite内存数据库进行测试
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 禁用CSRF保护以便测试
    WTF_CSRF_ENABLED = False
    
    # 日志级别
    LOG_LEVEL = 'DEBUG'
    
    # 文件清理配置
    EXPORT_DEFAULT_PATH = './test_exports/'
    FILE_CLEANUP_RETENTION_DAYS = 7
