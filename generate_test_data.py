#!/usr/bin/env python3
"""
生成百万级测试数据和关联查询SQL
为以下表生成数据：
- MW_ORDER_WORK (100万)
- MW_ORDER_WORK_RELATED (100万)
- MW_ORDER_CIRCULATE (100万)
- MW_ORDER_CIRCULATE_INFO (200万)
- MW_ORDER_PUBLIC_INCIDENT (100万)
"""

import random
from datetime import datetime, timedelta
import os

# 配置
DB_NAME = 'task_scheduler_dev'
OUTPUT_DIR = '/Users/linziwang/Downloads'

# 生成随机工单号
def generate_order_number(prefix, index):
    num = 100000 + index % 900000
    return f"{prefix}-{num:06d}"

# 生成随机时间（最近2年）
def random_time():
    start = datetime(2024, 1, 1)
    end = datetime(2026, 4, 21)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

# 生成随机中文描述
def random_description():
    prefixes = ['无线网', '传输网', '集客', '互联网', '核心网']
    suffixes = ['根因网元名称追单成功', '电路代号追单成功', '工单管控追单成功', '事件名称追单成功', '触发网元IP追单成功']
    return f"{random.choice(prefixes)}={random.choice(suffixes)}"

print("=" * 80)
print("开始生成百万级测试数据...")
print("=" * 80)

# ============================================
# 1. 生成MW_ORDER_WORK表数据 (100万条)
# ============================================
print("\n[1/5] 生成 MW_ORDER_WORK 表数据 (1,000,000 条)...")
work_sql_file = os.path.join(OUTPUT_DIR, 'MW_ORDER_WORK_data.sql')
with open(work_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- MW_ORDER_WORK 表数据\n")
    f.write("INSERT INTO `MW_ORDER_WORK` (`ID`, `SHEET_ID`, `TITLE`, `STATUS`, `PRIORITY`, `CREATE_TIME`, `UPDATE_TIME`, `CREATOR`) VALUES\n")
    
    for i in range(1000000):
        sheet_id = generate_order_number('FJ-076', i)
        title = f"工单-{sheet_id}"
        status = random.choice(['待处理', '处理中', '已完成', '已关闭'])
        priority = random.choice(['高', '中', '低'])
        create_time = random_time()
        update_time = create_time + timedelta(hours=random.randint(1, 72))
        creator = f"user_{random.randint(1000, 9999)}"
        
        comma = "," if i < 999999 else ";"
        f.write(f"('{i+1}', '{sheet_id}', '{title}', '{status}', '{priority}', '{create_time}', '{update_time}', '{creator}'){comma}\n")
        
        if (i + 1) % 100000 == 0:
            print(f"  已生成 {i+1:,} 条...")

print(f"  ✓ 完成! 文件: {work_sql_file}")

# ============================================
# 2. 生成MW_ORDER_WORK_RELATED表数据 (100万条)
# ============================================
print("\n[2/5] 生成 MW_ORDER_WORK_RELATED 表数据 (1,000,000 条)...")
related_sql_file = os.path.join(OUTPUT_DIR, 'MW_ORDER_WORK_RELATED_data.sql')
with open(related_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- MW_ORDER_WORK_RELATED 表数据\n")
    f.write("INSERT INTO `MW_ORDER_WORK_RELATED` (`ID`, `SHEET_ID`, `RELATED_SHEET_ID`, `RELATION_TYPE`, `REMARK`, `CREATE_TIME`, `UPDATE_TIME`, `CREATOR`, `UPDATER`) VALUES\n")
    
    for i in range(1000000):
        sheet_id = generate_order_number('FJ-076', i)
        related_id = generate_order_number('FJ-076', random.randint(0, 999999))
        relation_type = random.choice(['追', '关', '联'])
        remark = random_description()
        create_time = random_time()
        update_time = create_time + timedelta(hours=random.randint(1, 24))
        creator = f"system_{random.randint(1, 100)}"
        
        comma = "," if i < 999999 else ";"
        f.write(f"('{i+1}', '{sheet_id}', '{related_id}', '{relation_type}', '{remark}', '{create_time}', '{update_time}', '{creator}', '{creator}'){comma}\n")
        
        if (i + 1) % 100000 == 0:
            print(f"  已生成 {i+1:,} 条...")

print(f"  ✓ 完成! 文件: {related_sql_file}")

# ============================================
# 3. 生成MW_ORDER_CIRCULATE表数据 (100万条)
# ============================================
print("\n[3/5] 生成 MW_ORDER_CIRCULATE 表数据 (1,000,000 条)...")
circulate_sql_file = os.path.join(OUTPUT_DIR, 'MW_ORDER_CIRCULATE_data.sql')
with open(circulate_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- MW_ORDER_CIRCULATE 表数据\n")
    f.write("INSERT INTO `MW_ORDER_CIRCULATE` (`ID`, `SHEET_ID`, `CIRCULATE_NO`, `STATUS`, `CREATE_TIME`, `UPDATE_TIME`, `CREATOR`) VALUES\n")
    
    for i in range(1000000):
        sheet_id = generate_order_number('FJ-076', i)
        circulate_no = f"CIRC-{random.randint(10000000, 99999999)}"
        status = random.choice(['流转中', '已完成', '已终止'])
        create_time = random_time()
        update_time = create_time + timedelta(hours=random.randint(1, 168))
        creator = f"user_{random.randint(1000, 9999)}"
        
        comma = "," if i < 999999 else ";"
        f.write(f"('{i+1}', '{sheet_id}', '{circulate_no}', '{status}', '{create_time}', '{update_time}', '{creator}'){comma}\n")
        
        if (i + 1) % 100000 == 0:
            print(f"  已生成 {i+1:,} 条...")

print(f"  ✓ 完成! 文件: {circulate_sql_file}")

# ============================================
# 4. 生成MW_ORDER_CIRCULATE_INFO表数据 (200万条)
# ============================================
print("\n[4/5] 生成 MW_ORDER_CIRCULATE_INFO 表数据 (2,000,000 条)...")
circulate_info_sql_file = os.path.join(OUTPUT_DIR, 'MW_ORDER_CIRCULATE_INFO_data.sql')
with open(circulate_info_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- MW_ORDER_CIRCULATE_INFO 表数据\n")
    f.write("INSERT INTO `MW_ORDER_CIRCULATE_INFO` (`ID`, `CIRCULATE_ID`, `NODE_NAME`, `NODE_STATUS`, `HANDLE_TIME`, `CREATOR`) VALUES\n")
    
    for i in range(2000000):
        circulate_id = random.randint(1, 1000000)
        node_name = random.choice(['工单创建', '技术审核', '现场处理', '结果验证', '工单关闭'])
        node_status = random.choice(['已完成', '进行中', '待处理', '已跳过'])
        handle_time = random_time()
        creator = f"user_{random.randint(1000, 9999)}"
        
        comma = "," if i < 1999999 else ";"
        f.write(f"('{i+1}', '{circulate_id}', '{node_name}', '{node_status}', '{handle_time}', '{creator}'){comma}\n")
        
        if (i + 1) % 200000 == 0:
            print(f"  已生成 {i+1:,} 条...")

print(f"  ✓ 完成! 文件: {circulate_info_sql_file}")

# ============================================
# 5. 生成MW_ORDER_PUBLIC_INCIDENT表数据 (100万条)
# ============================================
print("\n[5/5] 生成 MW_ORDER_PUBLIC_INCIDENT 表数据 (1,000,000 条)...")
incident_sql_file = os.path.join(OUTPUT_DIR, 'MW_ORDER_PUBLIC_INCIDENT_data.sql')
with open(incident_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- MW_ORDER_PUBLIC_INCIDENT 表数据\n")
    f.write("INSERT INTO `MW_ORDER_PUBLIC_INCIDENT` (`ID`, `INCIDENT_NO`, `SHEET_ID`, `INCIDENT_TYPE`, `SEVERITY`, `OCCUR_TIME`, `CREATE_TIME`, `CREATOR`) VALUES\n")
    
    for i in range(1000000):
        incident_no = f"INC-{random.randint(100000000, 999999999)}"
        sheet_id = generate_order_number('FJ-076', random.randint(0, 999999))
        incident_type = random.choice(['设备故障', '网络中断', '性能下降', '安全事件', '配置错误'])
        severity = random.choice(['严重', '高', '中', '低'])
        occur_time = random_time()
        create_time = occur_time + timedelta(minutes=random.randint(5, 60))
        creator = f"system_{random.randint(1, 50)}"
        
        comma = "," if i < 999999 else ";"
        f.write(f"('{i+1}', '{incident_no}', '{sheet_id}', '{incident_type}', '{severity}', '{occur_time}', '{create_time}', '{creator}'){comma}\n")
        
        if (i + 1) % 100000 == 0:
            print(f"  已生成 {i+1:,} 条...")

print(f"  ✓ 完成! 文件: {incident_sql_file}")

# ============================================
# 6. 生成关联查询SQL示例
# ============================================
print("\n" + "=" * 80)
print("生成关联查询SQL示例...")
print("=" * 80)

query_sql_file = os.path.join(OUTPUT_DIR, 'million_data_queries.sql')
with open(query_sql_file, 'w', encoding='utf-8') as f:
    f.write(f"USE {DB_NAME};\n\n")
    f.write("-- ============================================\n")
    f.write("-- 百万级数据关联查询示例\n")
    f.write("-- ============================================\n\n")
    
    # 查询1: 工单及其关联工单
    f.write("-- 查询1: 工单及其关联工单信息 (百万级关联)\n")
    f.write("SELECT \n")
    f.write("    w.ID AS work_id,\n")
    f.write("    w.SHEET_ID AS work_sheet_id,\n")
    f.write("    w.TITLE AS work_title,\n")
    f.write("    w.STATUS AS work_status,\n")
    f.write("    r.RELATED_SHEET_ID,\n")
    f.write("    r.RELATION_TYPE,\n")
    f.write("    r.REMARK,\n")
    f.write("    w.CREATE_TIME\n")
    f.write("FROM MW_ORDER_WORK w\n")
    f.write("LEFT JOIN MW_ORDER_WORK_RELATED r ON w.SHEET_ID = r.SHEET_ID\n")
    f.write("WHERE w.CREATE_TIME >= '2025-01-01 00:00:00'\n")
    f.write("  AND w.CREATE_TIME < '2026-01-01 00:00:00'\n")
    f.write("ORDER BY w.CREATE_TIME DESC\n")
    f.write("LIMIT 100000;\n\n")
    
    # 查询2: 工单流转及节点信息
    f.write("-- 查询2: 工单流转及节点处理信息 (百万级关联)\n")
    f.write("SELECT \n")
    f.write("    w.SHEET_ID,\n")
    f.write("    w.TITLE,\n")
    f.write("    c.CIRCULATE_NO,\n")
    f.write("    c.STATUS AS circulate_status,\n")
    f.write("    ci.NODE_NAME,\n")
    f.write("    ci.NODE_STATUS,\n")
    f.write("    ci.HANDLE_TIME\n")
    f.write("FROM MW_ORDER_WORK w\n")
    f.write("INNER JOIN MW_ORDER_CIRCULATE c ON w.SHEET_ID = c.SHEET_ID\n")
    f.write("INNER JOIN MW_ORDER_CIRCULATE_INFO ci ON c.ID = ci.CIRCULATE_ID\n")
    f.write("WHERE w.CREATE_TIME >= '2025-01-01 00:00:00'\n")
    f.write("  AND w.CREATE_TIME < '2026-01-01 00:00:00'\n")
    f.write("ORDER BY ci.HANDLE_TIME DESC\n")
    f.write("LIMIT 100000;\n\n")
    
    # 查询3: 工单关联事件
    f.write("-- 查询3: 工单关联公共事件 (百万级关联)\n")
    f.write("SELECT \n")
    f.write("    w.SHEET_ID,\n")
    f.write("    w.TITLE,\n")
    f.write("    w.STATUS,\n")
    f.write("    i.INCIDENT_NO,\n")
    f.write("    i.INCIDENT_TYPE,\n")
    f.write("    i.SEVERITY,\n")
    f.write("    i.OCCUR_TIME\n")
    f.write("FROM MW_ORDER_WORK w\n")
    f.write("INNER JOIN MW_ORDER_PUBLIC_INCIDENT i ON w.SHEET_ID = i.SHEET_ID\n")
    f.write("WHERE w.CREATE_TIME >= '2025-01-01 00:00:00'\n")
    f.write("  AND w.CREATE_TIME < '2026-01-01 00:00:00'\n")
    f.write("ORDER BY i.OCCUR_TIME DESC\n")
    f.write("LIMIT 100000;\n\n")
    
    # 查询4: 完整关联查询 (五表关联)
    f.write("-- 查询4: 完整关联查询 (五表关联，百万级数据)\n")
    f.write("SELECT \n")
    f.write("    w.ID AS work_id,\n")
    f.write("    w.SHEET_ID,\n")
    f.write("    w.TITLE,\n")
    f.write("    w.STATUS AS work_status,\n")
    f.write("    r.RELATED_SHEET_ID,\n")
    f.write("    r.RELATION_TYPE,\n")
    f.write("    c.CIRCULATE_NO,\n")
    f.write("    c.STATUS AS circulate_status,\n")
    f.write("    ci.NODE_NAME,\n")
    f.write("    ci.NODE_STATUS,\n")
    f.write("    i.INCIDENT_NO,\n")
    f.write("    i.INCIDENT_TYPE,\n")
    f.write("    i.SEVERITY,\n")
    f.write("    w.CREATE_TIME\n")
    f.write("FROM MW_ORDER_WORK w\n")
    f.write("LEFT JOIN MW_ORDER_WORK_RELATED r ON w.SHEET_ID = r.SHEET_ID\n")
    f.write("LEFT JOIN MW_ORDER_CIRCULATE c ON w.SHEET_ID = c.SHEET_ID\n")
    f.write("LEFT JOIN MW_ORDER_CIRCULATE_INFO ci ON c.ID = ci.CIRCULATE_ID\n")
    f.write("LEFT JOIN MW_ORDER_PUBLIC_INCIDENT i ON w.SHEET_ID = i.SHEET_ID\n")
    f.write("WHERE w.CREATE_TIME >= '2025-01-01 00:00:00'\n")
    f.write("  AND w.CREATE_TIME < '2026-01-01 00:00:00'\n")
    f.write("ORDER BY w.CREATE_TIME DESC\n")
    f.write("LIMIT 100000;\n\n")
    
    # 查询5: 统计查询
    f.write("-- 查询5: 数据统计 (百万级)\n")
    f.write("SELECT \n")
    f.write("    DATE(w.CREATE_TIME) AS work_date,\n")
    f.write("    w.STATUS,\n")
    f.write("    COUNT(DISTINCT w.ID) AS work_count,\n")
    f.write("    COUNT(DISTINCT r.ID) AS related_count,\n")
    f.write("    COUNT(DISTINCT c.ID) AS circulate_count,\n")
    f.write("    COUNT(DISTINCT i.ID) AS incident_count\n")
    f.write("FROM MW_ORDER_WORK w\n")
    f.write("LEFT JOIN MW_ORDER_WORK_RELATED r ON w.SHEET_ID = r.SHEET_ID\n")
    f.write("LEFT JOIN MW_ORDER_CIRCULATE c ON w.SHEET_ID = c.SHEET_ID\n")
    f.write("LEFT JOIN MW_ORDER_PUBLIC_INCIDENT i ON w.SHEET_ID = i.SHEET_ID\n")
    f.write("WHERE w.CREATE_TIME >= '2025-01-01 00:00:00'\n")
    f.write("  AND w.CREATE_TIME < '2026-01-01 00:00:00'\n")
    f.write("GROUP BY DATE(w.CREATE_TIME), w.STATUS\n")
    f.write("ORDER BY work_date DESC;\n\n")

print(f"  ✓ 完成! 文件: {query_sql_file}")

# ============================================
# 汇总信息
# ============================================
print("\n" + "=" * 80)
print("数据生成完成！")
print("=" * 80)
print(f"\n生成的文件:")
print(f"  1. {work_sql_file}")
print(f"     - MW_ORDER_WORK: 1,000,000 条")
print(f"\n  2. {related_sql_file}")
print(f"     - MW_ORDER_WORK_RELATED: 1,000,000 条")
print(f"\n  3. {circulate_sql_file}")
print(f"     - MW_ORDER_CIRCULATE: 1,000,000 条")
print(f"\n  4. {circulate_info_sql_file}")
print(f"     - MW_ORDER_CIRCULATE_INFO: 2,000,000 条")
print(f"\n  5. {incident_sql_file}")
print(f"     - MW_ORDER_PUBLIC_INCIDENT: 1,000,000 条")
print(f"\n  6. {query_sql_file}")
print(f"     - 关联查询SQL示例 (5个查询)")
print(f"\n总计: 6,000,000 条记录")
print("\n导入命令:")
print(f"  mysql -u用户名 -p {DB_NAME} < {work_sql_file}")
print(f"  mysql -u用户名 -p {DB_NAME} < {related_sql_file}")
print(f"  mysql -u用户名 -p {DB_NAME} < {circulate_sql_file}")
print(f"  mysql -u用户名 -p {DB_NAME} < {circulate_info_sql_file}")
print(f"  mysql -u用户名 -p {DB_NAME} < {incident_sql_file}")
print("=" * 80)
