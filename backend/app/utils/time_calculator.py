"""
时间参数计算工具
支持固定时间和相对时间的计算
"""
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_time_param(param_config):
    """
    根据配置计算实际时间值
    
    Args:
        param_config (dict): 时间参数配置
            - type: 'fixed' 或 'relative'
            - value: 固定时间字符串（type=fixed时使用）
            - offset_days: 偏移天数（type=relative时使用）
            - time_of_day: 具体时间，格式 HH:MM:SS（可选）
    
    Returns:
        str: 格式化后的时间字符串 'YYYY-MM-DD HH:MM:SS'
    
    Examples:
        >>> calculate_time_param({'type': 'fixed', 'value': '2025-01-01 00:00:00'})
        '2025-01-01 00:00:00'
        
        >>> calculate_time_param({'type': 'relative', 'offset_days': -1, 'time_of_day': '23:59:59'})
        '2026-04-19 23:59:59'  # 假设当前是2026-04-20
    """
    param_type = param_config.get('type', 'fixed')
    
    if param_type == 'fixed':
        # 固定时间（兼容 fixed_time 和 value 两种字段）
        fixed_value = param_config.get('fixed_time') or param_config.get('value')
        if not fixed_value:
            raise ValueError(f"Fixed time value is empty for param: {param_config}")
        return fixed_value
    
    elif param_type == 'relative':
        # 相对时间
        offset_days = param_config.get('offset_days', 0)
        time_of_day = param_config.get('time_of_day', '00:00:00')
        
        # 计算基准日期
        base_date = datetime.now() + timedelta(days=offset_days)
        
        # 解析时间部分
        try:
            time_parts = time_of_day.split(':')
            hour = int(time_parts[0]) if len(time_parts) > 0 else 0
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            
            # 组合日期和时间
            result_datetime = base_date.replace(hour=hour, minute=minute, second=second, microsecond=0)
            
            return result_datetime.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid time_of_day format: {time_of_day}, error: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported time param type: {param_type}")


def calculate_all_time_params(time_params_config):
    """
    计算所有时间参数
    
    Args:
        time_params_config (dict): 时间参数配置字典
            例如: {
                'start_time': {'type': 'fixed', 'value': '2025-01-01 00:00:00'},
                'end_time': {'type': 'relative', 'offset_days': -1, 'time_of_day': '23:59:59'}
            }
    
    Returns:
        dict: 计算后的时间参数字典
            例如: {
                'start_time': '2025-01-01 00:00:00',
                'end_time': '2026-04-19 23:59:59'
            }
    """
    logger.debug(f"Calculating time params for {len(time_params_config)} parameters")
    
    result = {}
    for param_name, param_config in time_params_config.items():
        result[param_name] = calculate_time_param(param_config)
        logger.debug(f"Calculated {param_name}: {result[param_name]}")
    
    logger.info(f"All time params calculated: {list(result.keys())}")
    return result
