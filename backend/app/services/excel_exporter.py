"""
Excel导出服务
支持大文件分片、日期格式化等
"""
import os
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_dataframe_for_excel(df):
    """
    格式化DataFrame以便更好地导出到Excel
    
    Args:
        df (pd.DataFrame): 原始DataFrame
        
    Returns:
        pd.DataFrame: 格式化后的DataFrame
    """
    if df.empty:
        return df
    
    # 创建副本避免修改原数据
    formatted_df = df.copy()
    
    # 格式化datetime列
    for col in formatted_df.columns:
        if pd.api.types.is_datetime64_any_dtype(formatted_df[col]):
            formatted_df[col] = formatted_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # 处理None/NaN值
    formatted_df = formatted_df.fillna('')
    
    return formatted_df


def export_to_excel(df, filepath, filename_prefix, max_rows_per_file=50000):
    """
    将DataFrame导出为Excel文件，支持大文件分片
    
    Args:
        df (pd.DataFrame): 要导出的数据
        filepath (str): 导出目录路径
        filename_prefix (str): 文件名前缀
        max_rows_per_file (int): 单个文件最大行数，超过则分片
        
    Returns:
        list: 生成的文件路径列表
    """
    import time
    start_time = time.time()
    
    # 确保导出目录存在
    logger.debug(f"Ensuring export directory exists: {filepath}")
    os.makedirs(filepath, exist_ok=True)
    
    # 生成时间戳
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 格式化数据
    logger.debug("Formatting DataFrame for Excel")
    formatted_df = format_dataframe_for_excel(df)
    total_rows = len(formatted_df)
    
    logger.info(f"Starting Excel export: {total_rows} rows, prefix={filename_prefix}")
    
    # 判断是否需要分片
    if total_rows <= max_rows_per_file:
        # 不需要分片
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        full_path = os.path.join(filepath, filename)
        
        logger.info(f"Creating single Excel file: {full_path}")
        _write_excel(formatted_df, full_path)
        
        duration = time.time() - start_time
        file_size = get_file_size(full_path)
        logger.info(f"Excel file created successfully: {full_path}, size={file_size} bytes, duration={duration:.2f}s")
        return [full_path]
    
    else:
        # 需要分片
        file_paths = []
        num_parts = (total_rows + max_rows_per_file - 1) // max_rows_per_file
        
        logger.info(f"Splitting data into {num_parts} parts (max {max_rows_per_file} rows per file)")
        
        for i in range(num_parts):
            part_start = time.time()
            start_idx = i * max_rows_per_file
            end_idx = min((i + 1) * max_rows_per_file, total_rows)
            
            part_df = formatted_df.iloc[start_idx:end_idx]
            
            filename = f"{filename_prefix}_{timestamp}_part{i+1}.xlsx"
            full_path = os.path.join(filepath, filename)
            
            logger.debug(f"Writing part {i+1}/{num_parts}: rows {start_idx}-{end_idx}")
            _write_excel(part_df, full_path)
            file_paths.append(full_path)
            
            part_duration = time.time() - part_start
            logger.info(f"Part {i+1}/{num_parts} created: {full_path}, duration={part_duration:.2f}s")
        
        total_duration = time.time() - start_time
        total_size = sum(get_file_size(fp) for fp in file_paths)
        logger.info(f"All parts exported: {len(file_paths)} files, total_size={total_size} bytes, duration={total_duration:.2f}s")
        
        return file_paths


def _write_excel(df, filepath):
    """
    写入Excel文件
    
    Args:
        df (pd.DataFrame): 数据
        filepath (str): 文件路径
    """
    try:
        # 使用openpyxl引擎
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # 获取workbook和worksheet
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # 自动调整列宽（可选）
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                # 设置列宽（最小10，最大50）
                adjusted_width = min(max(max_length + 2, 10), 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
    except Exception as e:
        logger.error(f"Failed to write Excel file: {str(e)}")
        raise


def get_file_size(filepath):
    """
    获取文件大小（字节）
    
    Args:
        filepath (str): 文件路径
        
    Returns:
        int: 文件大小
    """
    try:
        return os.path.getsize(filepath)
    except:
        return 0
