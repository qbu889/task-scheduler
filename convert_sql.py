#!/usr/bin/env python3
"""
将Oracle风格的SQL INSERT语句转换为MySQL兼容格式
- 移除表名和列名的单引号
- 映射列名
- 处理重复列的值（取第一个非NULL值）
"""

import re

# 列名映射关系（Oracle列名 -> MySQL列名）
COLUMN_MAPPING = {
    'ID': 'ID',
    'SHEET_ID': 'SHEET_ID',
    'SON_EVENT_NUMBER': 'RELATED_SHEET_ID',
    'MAIN_EVENT_NUMBER': 'RELATED_SHEET_ID',
    'CREATE_TIME': 'CREATE_TIME',
    'CREATE_USER': 'CREATOR',
    'JOIN_TYPE': 'RELATION_TYPE',
    'JOIN_EXPLAIN': 'REMARK'
}

# MySQL表的列顺序
MYSQL_COLUMNS = ['ID', 'SHEET_ID', 'RELATED_SHEET_ID', 'RELATION_TYPE', 'REMARK', 'CREATE_TIME', 'UPDATE_TIME', 'CREATOR', 'UPDATER']

def parse_values(values_str):
    """解析VALUES中的值，处理引号和括号"""
    values_str = values_str.strip()
    # 移除开头的括号和结尾的分号+括号
    if values_str.startswith('('):
        values_str = values_str[1:]
    if values_str.endswith(');'):
        values_str = values_str[:-2]
    elif values_str.endswith(')'):
        values_str = values_str[:-1]
    
    values = []
    current = ''
    in_quote = False
    quote_char = None
    
    for char in values_str:
        if char in ("'", '"') and not in_quote:
            in_quote = True
            quote_char = char
            current += char
        elif char == quote_char and in_quote:
            in_quote = False
            quote_char = None
            current += char
        elif char == ',' and not in_quote:
            values.append(current.strip())
            current = ''
        else:
            current += char
    
    if current:
        values.append(current.strip())
    
    return values

def convert_sql(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    converted_lines = []
    error_count = 0
    
    for i, line in enumerate(lines, 1):
        match = re.match(
            r"insert into '([^']+)'\.'([^']+)' \(([^)]+)\) values (.+)",
            line.strip()
        )
        
        if match:
            db_name = match.group(1)
            table_name = match.group(2)
            columns_str = match.group(3)
            values_str = match.group(4)
            
            # 解析原始列和值
            original_columns = [col.strip().strip("'") for col in columns_str.split(',')]
            original_values = parse_values(values_str)
            
            # 创建列到值的映射
            column_value_map = {}
            for col, val in zip(original_columns, original_values):
                if col in COLUMN_MAPPING:
                    mapped_col = COLUMN_MAPPING[col]
                    # 如果是重复列，只保留第一个非NULL值
                    if mapped_col not in column_value_map:
                        column_value_map[mapped_col] = val
                    elif column_value_map[mapped_col] == 'null' and val != 'null':
                        column_value_map[mapped_col] = val
                else:
                    column_value_map[col] = val
                    error_count += 1
            
            # 按MySQL表结构顺序生成列和值
            mysql_columns = []
            mysql_values = []
            for col in MYSQL_COLUMNS:
                if col in column_value_map:
                    mysql_columns.append(col)
                    mysql_values.append(column_value_map[col])
            
            columns_fixed = ', '.join(mysql_columns)
            values_fixed = ', '.join(mysql_values)
            
            # 重新组装SQL
            converted = f'insert into {db_name}.{table_name} ({columns_fixed}) values ({values_fixed})'
            converted_lines.append(converted + '\n')
        else:
            converted_lines.append(line)
        
        if i % 100000 == 0:
            print(f'已处理 {i} 行...')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(converted_lines)
    
    print(f'\n✅ 转换完成！')
    print(f'输入文件: {input_file}')
    print(f'输出文件: {output_file}')
    print(f'总行数: {len(converted_lines)}')
    print(f'列映射警告: {error_count} 行')
    print(f'\nMySQL表列顺序: {", ".join(MYSQL_COLUMNS)}')

if __name__ == '__main__':
    input_file = '/Users/linziwang/Downloads/MW_ORDER_WORK_RELATED.sql'
    output_file = '/Users/linziwang/Downloads/MW_ORDER_WORK_RELATED_mysql.sql'
    convert_sql(input_file, output_file)
