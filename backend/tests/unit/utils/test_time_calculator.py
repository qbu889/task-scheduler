"""
时间计算器单元测试
"""
import pytest
from app.utils.time_calculator import calculate_time_param, calculate_all_time_params
from datetime import datetime


class TestTimeCalculator:
    """时间计算器测试类"""
    
    def test_fixed_time(self):
        """测试固定时间计算"""
        config = {
            'type': 'fixed',
            'value': '2025-01-01 00:00:00'
        }
        result = calculate_time_param(config)
        assert result == '2025-01-01 00:00:00'
    
    def test_relative_time_yesterday(self):
        """测试相对时间 - 昨天"""
        config = {
            'type': 'relative',
            'offset_days': -1,
            'time_of_day': '23:59:59'
        }
        result = calculate_time_param(config)
        
        # 验证格式
        datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
        # 验证时间是23:59:59
        assert result.endswith('23:59:59')
    
    def test_relative_time_today(self):
        """测试相对时间 - 今天"""
        config = {
            'type': 'relative',
            'offset_days': 0,
            'time_of_day': '00:00:00'
        }
        result = calculate_time_param(config)
        
        # 验证格式
        datetime.strptime(result, '%Y-%m-%d %H:%M:%S')
    
    def test_calculate_all_params(self):
        """测试批量计算时间参数"""
        config = {
            'start_time': {
                'type': 'fixed',
                'value': '2025-01-01 00:00:00'
            },
            'end_time': {
                'type': 'relative',
                'offset_days': -1,
                'time_of_day': '23:59:59'
            }
        }
        
        result = calculate_all_time_params(config)
        
        assert 'start_time' in result
        assert 'end_time' in result
        assert result['start_time'] == '2025-01-01 00:00:00'
    
    def test_invalid_type(self):
        """测试无效的类型"""
        config = {
            'type': 'invalid',
        }
        
        with pytest.raises(ValueError):
            calculate_time_param(config)
    
    def test_invalid_time_format(self):
        """测试无效的时间格式"""
        config = {
            'type': 'relative',
            'offset_days': -1,
            'time_of_day': 'invalid'
        }
        
        with pytest.raises(ValueError):
            calculate_time_param(config)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
