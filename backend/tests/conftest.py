"""
pytest配置文件
"""
import pytest
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_dataframe():
    """提供示例DataFrame"""
    import pandas as pd
    return pd.DataFrame({
        'name': ['张三', '李四', '王五'],
        'age': [25, 30, 35],
        'city': ['北京', '上海', '广州']
    })


@pytest.fixture
def sample_task_config():
    """提供示例任务配置"""
    return {
        'task_name': '测试任务',
        'datasource_type': 'mysql',
        'datasource_config': {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db'
        },
        'sql_template': 'SELECT * FROM test_table WHERE create_time BETWEEN :start_time AND :end_time',
        'time_params': {
            'start_time': {
                'type': 'fixed',
                'value': '2025-01-01 00:00:00'
            },
            'end_time': {
                'type': 'relative',
                'offset_days': -1,
                'time_of_day': '23:59:59'
            }
        },
        'cron_expression': '0 9 * * *',
        'export_path': '/exports/',
        'filename_prefix': 'test_export',
        'max_rows': 50000,
        'batch_size': 5000,
        'is_enabled': 1
    }
