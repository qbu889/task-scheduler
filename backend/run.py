"""
应用启动入口
"""
import os
import sys
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
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    main()
