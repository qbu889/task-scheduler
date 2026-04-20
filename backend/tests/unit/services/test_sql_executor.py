"""
SQL执行引擎单元测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from app.services.sql_executor import execute_sql, _create_engine_from_config


class TestSqlExecutor:
    """SQL执行引擎测试类"""
    
    def test_create_mysql_engine(self):
        """测试创建MySQL引擎"""
        config = {
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db',
            'charset': 'utf8mb4'
        }
        
        with patch('app.services.sql_executor.create_engine') as mock_engine:
            engine = _create_engine_from_config(config)
            assert mock_engine.called
    
    def test_create_dm_engine(self):
        """测试创建达梦引擎"""
        config = {
            'type': 'dm',
            'host': '127.0.0.1',
            'port': 5236,
            'user': 'SYSDBA',
            'password': 'password',
            'database': 'TASK_DB'
        }
        
        with patch('app.services.sql_executor.create_engine') as mock_engine:
            engine = _create_engine_from_config(config)
            assert mock_engine.called
    
    def test_execute_sql_success(self):
        """测试SQL执行成功"""
        datasource_config = {
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db'
        }
        sql_template = 'SELECT * FROM test_table'
        time_params = {}
        
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['张三', '李四', '王五']
        })
        
        with patch('app.services.sql_executor._create_engine_from_config') as mock_engine_func:
            mock_engine = Mock()
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
            mock_engine_func.return_value = mock_engine
            
            with patch('pandas.read_sql_query', return_value=mock_df):
                result_df, record_count = execute_sql(
                    datasource_config, 
                    sql_template, 
                    time_params
                )
                
                assert isinstance(result_df, pd.DataFrame)
                assert record_count == 3
    
    def test_execute_sql_with_time_params(self):
        """测试带时间参数的SQL执行"""
        datasource_config = {
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db'
        }
        sql_template = 'SELECT * FROM test WHERE create_time BETWEEN :start_time AND :end_time'
        time_params = {
            'start_time': '2025-01-01 00:00:00',
            'end_time': '2025-01-31 23:59:59'
        }
        
        mock_df = pd.DataFrame({'id': [1]})
        
        with patch('app.services.sql_executor._create_engine_from_config') as mock_engine_func:
            mock_engine = Mock()
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
            mock_engine_func.return_value = mock_engine
            
            with patch('pandas.read_sql_query', return_value=mock_df):
                result_df, record_count = execute_sql(
                    datasource_config,
                    sql_template,
                    time_params
                )
                
                assert record_count == 1
    
    def test_execute_sql_empty_result(self):
        """测试SQL执行返回空结果"""
        datasource_config = {
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db'
        }
        sql_template = 'SELECT * FROM test_table WHERE 1=0'
        time_params = {}
        
        mock_df = pd.DataFrame()
        
        with patch('app.services.sql_executor._create_engine_from_config') as mock_engine_func:
            mock_engine = Mock()
            mock_conn = Mock()
            mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
            mock_engine_func.return_value = mock_engine
            
            with patch('pandas.read_sql_query', return_value=mock_df):
                result_df, record_count = execute_sql(
                    datasource_config,
                    sql_template,
                    time_params
                )
                
                assert result_df.empty
                assert record_count == 0
    
    def test_execute_sql_error(self):
        """测试SQL执行错误处理"""
        datasource_config = {
            'type': 'mysql',
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '12345678',
            'database': 'test_db'
        }
        sql_template = 'INVALID SQL'
        time_params = {}
        
        with patch('app.services.sql_executor._create_engine_from_config') as mock_engine_func:
            mock_engine = Mock()
            mock_engine.connect.side_effect = Exception('Connection failed')
            mock_engine_func.return_value = mock_engine
            
            with pytest.raises(Exception):
                execute_sql(datasource_config, sql_template, time_params)
