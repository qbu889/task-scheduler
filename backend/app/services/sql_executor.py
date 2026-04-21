"""
SQL执行引擎
支持MySQL和达梦数据库，支持分页查询和大结果集处理
"""
import pandas as pd
from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)


def _create_engine_from_config(datasource_config):
    """
    根据数据源配置创建SQLAlchemy引擎
    
    Args:
        datasource_config (dict): 数据源配置
        
    Returns:
        SQLAlchemy Engine
    """
    datasource_type = datasource_config.get('type', 'mysql')
    
    if datasource_type == 'mysql':
        # MySQL连接
        host = datasource_config.get('host', '127.0.0.1')
        port = datasource_config.get('port', 3306)
        user = datasource_config.get('user', 'root')
        password = datasource_config.get('password', '')
        database = datasource_config.get('database', '')
        charset = datasource_config.get('charset', 'utf8mb4')
        
        connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset={charset}"
        
    elif datasource_type == 'dm':
        # 达梦数据库连接
        host = datasource_config.get('host', '127.0.0.1')
        port = datasource_config.get('port', 5236)
        user = datasource_config.get('user', 'SYSDBA')
        password = datasource_config.get('password', '')
        database = datasource_config.get('database', '')
        charset = datasource_config.get('charset', 'utf8')
        
        connection_url = f"dm+dmPython://{user}:{password}@{host}:{port}/{database}?charset={charset}"
    
    else:
        raise ValueError(f"Unsupported datasource type: {datasource_type}")
    
    engine = create_engine(
        connection_url,
        pool_size=10,  # 增加连接池大小
        max_overflow=20,  # 允许额外连接数
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={
            'connect_timeout': 60,  # 连接超时60秒
            'read_timeout': 300,  # 读取超时300秒（5分钟）
            'write_timeout': 300  # 写入超时300秒
        },
        execution_options={
            'stream_results': True  # 启用流式结果，减少内存占用
        }
    )
    
    return engine


def replace_sql_placeholders(sql_template, time_params):
    """
    替换SQL模板中的占位符
    
    Args:
        sql_template (str): SQL模板，包含 :param_name 格式的占位符
        time_params (dict): 时间参数字典，例如 {'start_time': '2025-01-01 00:00:00'}
        
    Returns:
        str: 替换后的SQL语句
    """
    result_sql = sql_template
    
    for param_name, param_value in time_params.items():
        # 替换占位符 :param_name 为 'value'
        placeholder = f":{param_name}"
        # 确保时间值用引号包裹
        formatted_value = f"'{param_value}'"
        result_sql = result_sql.replace(placeholder, formatted_value)
    
    return result_sql


def execute_sql(datasource_config, sql_template, time_params=None, batch_size=10000):
    """
    执行SQL查询并返回DataFrame
    
    Args:
        datasource_config (dict): 数据源配置
        sql_template (str): SQL模板
        time_params (dict): 时间参数（用于替换占位符）
        batch_size (int): 分页大小（默认增加到10000）
        
    Returns:
        tuple: (DataFrame, total_rows, final_sql)
    """
    engine = None
    try:
        # 替换SQL占位符
        if time_params:
            final_sql = replace_sql_placeholders(sql_template, time_params)
        else:
            final_sql = sql_template
        
        logger.info(f"Executing SQL query (preview): {final_sql[:200]}...")
        logger.debug(f"Full SQL: {final_sql}")
        
        # 创建数据库引擎
        logger.debug("Creating database engine")
        engine = _create_engine_from_config(datasource_config)
        
        # 执行查询（使用pandas直接读取）
        logger.debug("Executing query via pandas")
        
        # 对于大数据量，使用chunksize分块读取
        if batch_size and batch_size > 0:
            chunks = pd.read_sql_query(final_sql, engine, chunksize=batch_size)
            df_list = []
            for chunk in chunks:
                df_list.append(chunk)
            if df_list:
                df = pd.concat(df_list, ignore_index=True)
            else:
                df = pd.DataFrame()
        else:
            df = pd.read_sql_query(final_sql, engine)
        
        total_rows = len(df)
        logger.info(f"Query completed successfully: {total_rows} rows fetched")
        
        return df, total_rows, final_sql
        
    except Exception as e:
        logger.error(f"SQL execution failed: {str(e)}", exc_info=True)
        raise
    finally:
        if engine:
            logger.debug("Disposing database engine")
            engine.dispose()


def execute_sql_paginated(datasource_config, sql_template, time_params=None, batch_size=10000, max_rows=100000):
    """
    分页执行SQL查询（适用于大数据量）
    
    Args:
        datasource_config (dict): 数据源配置
        sql_template (str): SQL模板（不应包含LIMIT/OFFSET）
        time_params (dict): 时间参数
        batch_size (int): 每页大小（默认增加到10000）
        max_rows (int): 最大记录数限制
        
    Returns:
        tuple: (DataFrame, total_rows)
    """
    engine = None
    try:
        # 替换SQL占位符
        if time_params:
            base_sql = replace_sql_placeholders(sql_template, time_params)
        else:
            base_sql = sql_template
        
        logger.info(f"Executing paginated SQL with batch_size={batch_size}, max_rows={max_rows}")
        
        # 创建数据库引擎
        engine = _create_engine_from_config(datasource_config)
        
        # 先查询总数
        count_sql = f"SELECT COUNT(*) as total FROM ({base_sql}) as subquery"
        total_df = pd.read_sql_query(count_sql, engine)
        total_rows = int(total_df.iloc[0]['total'])
        
        logger.info(f"Total rows to fetch: {total_rows}")
        
        # 限制最大记录数
        if total_rows > max_rows:
            logger.warning(f"Total rows {total_rows} exceeds max_rows {max_rows}, limiting to {max_rows}")
            total_rows = max_rows
        
        # 如果数据量小，直接查询
        if total_rows <= batch_size:
            df = pd.read_sql_query(base_sql, engine)
            return df, len(df)
        
        # 分批查询
        all_dfs = []
        offset = 0
        
        while offset < total_rows:
            # 添加LIMIT和OFFSET
            paginated_sql = f"{base_sql} LIMIT {batch_size} OFFSET {offset}"
            
            logger.info(f"Fetching batch: offset={offset}, limit={batch_size}")
            batch_df = pd.read_sql_query(paginated_sql, engine)
            
            if len(batch_df) == 0:
                break
            
            all_dfs.append(batch_df)
            offset += batch_size
            
            # 检查是否达到最大记录数
            if len(all_dfs) * batch_size >= max_rows:
                break
        
        # 合并所有批次
        if all_dfs:
            result_df = pd.concat(all_dfs, ignore_index=True)
            return result_df, len(result_df)
        else:
            return pd.DataFrame(), 0
        
    except Exception as e:
        logger.error(f"Paginated SQL execution failed: {str(e)}")
        raise
    finally:
        if engine:
            engine.dispose()
