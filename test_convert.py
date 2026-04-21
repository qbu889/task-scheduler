#!/usr/bin/env python3
import re

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

MYSQL_COLUMNS = ['ID', 'SHEET_ID', 'RELATED_SHEET_ID', 'RELATION_TYPE', 'REMARK', 'CREATE_TIME', 'UPDATE_TIME', 'CREATOR', 'UPDATER']

line = "insert into 'task_scheduler_dev'.'MW_ORDER_WORK_RELATED' ('ID', 'SHEET_ID', 'SON_EVENT_NUMBER', 'MAIN_EVENT_NUMBER', 'CREATE_TIME', 'CREATE_USER', 'JOIN_TYPE', 'JOIN_EXPLAIN') values (3477553, 'FJ-076-20251109-0371', '276242844', '275986694', '2025-11-10 00:00:07', null, '追', '无线网=根因网元名称+根因网元类型追单成功');"

match = re.match(r"insert into '([^']+)'.'([^']+)' \(([^)]+)\) values (.+)", line.strip())
if match:
    columns_str = match.group(3)
    values_str = match.group(4)
    
    original_columns = [col.strip().strip("'") for col in columns_str.split(',')]
    
    print('原始列:', original_columns)
    print('列数:', len(original_columns))
    
    # 解析值
    def parse_values(values_str):
        values_str = values_str.strip()
        if values_str.startswith('(') and values_str.endswith(');'):
            values_str = values_str[1:-2]
        
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
    
    original_values = parse_values(values_str)
    print('\n原始值:', original_values)
    print('值数:', len(original_values))
    
    # 创建映射
    column_value_map = {}
    for col, val in zip(original_columns, original_values):
        if col in COLUMN_MAPPING:
            mapped_col = COLUMN_MAPPING[col]
            if mapped_col not in column_value_map:
                column_value_map[mapped_col] = val
            elif column_value_map[mapped_col] == 'null' and val != 'null':
                column_value_map[mapped_col] = val
        else:
            column_value_map[col] = val
    
    print('\n列值映射:')
    for k, v in column_value_map.items():
        print(f'  {k}: {v}')
    
    # 按MySQL顺序输出
    mysql_columns = []
    mysql_values = []
    for col in MYSQL_COLUMNS:
        if col in column_value_map:
            mysql_columns.append(col)
            mysql_values.append(column_value_map[col])
    
    print(f'\nMySQL列 ({len(mysql_columns)}个):', mysql_columns)
    print(f'MySQL值 ({len(mysql_values)}个):', mysql_values)
