"""
应用启动入口
"""
import os
import sys
from dotenv import load_dotenv
from app import create_app
from config import Config
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# 加载环境变量
# 先加载默认配置
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 根据环境加载特定配置文件
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    prod_env_file = os.path.join(os.path.dirname(__file__), '.env.production')
    if os.path.exists(prod_env_file):
        load_dotenv(prod_env_file, override=True)
        logger.info(f"Loaded production environment from .env.production")
elif env == 'development':
    dev_env_file = os.path.join(os.path.dirname(__file__), '.env.development')
    if os.path.exists(dev_env_file):
        load_dotenv(dev_env_file, override=True)
        logger.info(f"Loaded development environment from .env.development")


def main():
    """主函数"""
    # 获取环境配置
    env = os.getenv('FLASK_ENV', 'development')
    logger.info(f"Starting application in {env} mode")
    
    # 创建应用
    app = create_app()
    
    # 运行应用
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Server running on http://{host}:{port}")
    logger.info(f"Debug mode: {debug}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
