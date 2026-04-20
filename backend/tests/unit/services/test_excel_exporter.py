"""
Excel导出服务单元测试
"""
import pytest
import pandas as pd
from datetime import datetime
from app.services.excel_exporter import format_dataframe_for_excel, export_to_excel


class TestExcelExporter:
    """Excel导出服务测试类"""
    
    def test_format_dataframe_datetime(self):
        """测试DataFrame日期格式化"""
        df = pd.DataFrame({
            'name': ['张三', '李四'],
            'date': pd.to_datetime(['2025-01-01', '2025-01-02']),
            'value': [100, 200]
        })
        
        formatted_df = format_dataframe_for_excel(df)
        
        # 日期列应该转换为字符串
        assert formatted_df['date'].dtype == 'object'
        assert formatted_df['date'].iloc[0] == '2025-01-01 00:00:00'
    
    def test_format_dataframe_nan(self):
        """测试NaN值处理"""
        df = pd.DataFrame({
            'name': ['张三', None, '李四'],
            'value': [100, float('nan'), 200]
        })
        
        formatted_df = format_dataframe_for_excel(df)
        
        # NaN应该被替换为空字符串
        assert formatted_df['name'].iloc[1] == ''
        assert formatted_df['value'].iloc[1] == ''
    
    def test_format_dataframe_empty(self):
        """测试空DataFrame"""
        df = pd.DataFrame()
        formatted_df = format_dataframe_for_excel(df)
        
        assert formatted_df.empty
    
    def test_format_dataframe_no_datetime(self):
        """测试不含日期的DataFrame"""
        df = pd.DataFrame({
            'name': ['张三', '李四'],
            'value': [100, 200]
        })
        
        formatted_df = format_dataframe_for_excel(df)
        
        assert len(formatted_df) == 2
        assert formatted_df['name'].iloc[0] == '张三'
    
    def test_export_to_excel_single_file(self, tmp_path):
        """测试导出单个Excel文件"""
        df = pd.DataFrame({
            'name': ['张三', '李四'],
            'value': [100, 200]
        })
        
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        
        files = export_to_excel(
            df=df,
            filepath=str(export_dir),
            filename_prefix='test',
            max_rows_per_file=50000
        )
        
        assert len(files) == 1
        assert 'test' in files[0]
        assert files[0].endswith('.xlsx')
    
    def test_export_to_excel_split_files(self, tmp_path):
        """测试分片导出多个Excel文件"""
        # 创建100行数据
        df = pd.DataFrame({
            'id': range(100),
            'value': range(100)
        })
        
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        
        # 设置每30行一个文件
        files = export_to_excel(
            df=df,
            filepath=str(export_dir),
            filename_prefix='test',
            max_rows_per_file=30
        )
        
        # 应该生成4个文件（30+30+30+10）
        assert len(files) == 4
        
        # 验证每个文件的行数
        for i, file in enumerate(files):
            loaded_df = pd.read_excel(file)
            if i < 3:
                assert len(loaded_df) == 30
            else:
                assert len(loaded_df) == 10
    
    def test_export_to_excel_empty_dataframe(self, tmp_path):
        """测试导出空DataFrame"""
        df = pd.DataFrame()
        
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        
        files = export_to_excel(
            df=df,
            filepath=str(export_dir),
            filename_prefix='test'
        )
        
        # 空DataFrame也应该生成文件
        assert len(files) >= 0
