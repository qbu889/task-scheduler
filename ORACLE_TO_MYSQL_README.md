# Oracle SQL 到 MySQL 转换项目

## 项目概述
本项目包含将4个Oracle SQL表转换为MySQL格式所需的所有文件和脚本。

## 生成的文件

### 1. MySQL建表脚本
- **mysql_create_tables.sql** - 包含4个表的CREATE TABLE语句
  - MW_ORDER_CIRCULATE_INFO (工单流转信息表 - 163字段)
  - MW_ORDER_WORK (工单工作表 - 89字段)
  - MW_ORDER_PUBLIC_INCIDENT (公共事件表 - 169字段)
  - MW_ORDER_CIRCULATE (工单流转表 - 25字段)

### 2. 数据转换脚本
- **convert_oracle_to_mysql.py** - Python脚本,自动将Oracle SQL转换为MySQL格式
  - 转换引号(双引号 → 反引号)
  - 转换日期时间格式(去掉微秒)
  - 移除Schema前缀
  - 统一NULL值格式

### 3. 数据导入脚本
- **import_to_mysql.sh** - Bash脚本,一键完成建表和数据导入

### 4. 文档
- **MYSQL_IMPORT_GUIDE.md** - 详细的导入指南
- **ORACLE_TO_MYSQL_README.md** - 本文件

## 快速开始

### 方法一:使用自动化脚本(推荐)

1. **运行转换脚本**(已完成):
```bash
python3 convert_oracle_to_mysql.py
```
✓ 已转换4个文件,每个文件50条INSERT语句

2. **运行导入脚本**:
```bash
./import_to_mysql.sh
```
脚本会提示您输入MySQL密码,然后自动:
- 创建数据库
- 创建表
- 导入数据
- 验证数据

### 方法二:手动步骤

#### Step 1: 创建数据库
```sql
CREATE DATABASE IF NOT EXISTS monitorwo 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
USE monitorwo;
```

#### Step 2: 执行建表脚本
```bash
mysql -u root -p monitorwo < mysql_create_tables.sql
```

#### Step 3: 导入数据
```bash
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_INFO_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_WORK_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_PUBLIC_INCIDENT_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_mysql.sql
```

## 表结构说明

### MW_ORDER_CIRCULATE_INFO (工单流转信息表)
**主要用途**: 存储工单流转的详细信息
**关键字段**:
- ID: 主键
- LINK_ID: 关联ID
- SHEET_ID: 工单ID
- CREATE_TIME: 创建时间
- UPDATE_TIME: 更新时间
- 各种故障处理、检查、反馈相关字段

**索引**:
- PRIMARY KEY (ID)
- INDEX idx_link_id (LINK_ID)
- INDEX idx_sheet_id (SHEET_ID)
- INDEX idx_create_time (CREATE_TIME)
- INDEX idx_update_time (UPDATE_TIME)

### MW_ORDER_WORK (工单工作表)
**主要用途**: 存储工单的基本信息和工作状态
**关键字段**:
- SHEET_ID: 工单ID(主键)
- TITLE: 标题
- STATUS: 状态
- EVENT_NUMBER: 事件编号
- MAIN_NETSORT_ONE/TWO/THREE: 网络分类
- SEND_TIME: 派发时间
- CREATE_TIME: 创建时间

**索引**:
- PRIMARY KEY (SHEET_ID)
- INDEX idx_link_id (LINK_ID)
- INDEX idx_create_time (CREATE_TIME)
- INDEX idx_update_time (UPDATE_TIME)
- INDEX idx_status (STATUS)

### MW_ORDER_PUBLIC_INCIDENT (公共事件表)
**主要用途**: 存储公共事件和告警信息
**关键字段**:
- ID: 主键
- EVENT_ID: 事件ID
- EVENT_NUMBER: 事件编号
- EVENT_NAME: 事件名称
- ROOT_CAUSE_NE_NAME: 根因网元名称
- TRIGGER_NE_NAME: 触发网元名称
- EVENT_HAPPEN_TIME: 事件发生时间
- EVENT_CLEAN_TIME: 事件清除时间

**索引**:
- PRIMARY KEY (ID)
- INDEX idx_event_id (EVENT_ID)
- INDEX idx_sheet_id (SHEET_ID)
- INDEX idx_create_time (CREATE_TIME)
- INDEX idx_update_time (UPDATE_TIME)

### MW_ORDER_CIRCULATE (工单流转表)
**主要用途**: 存储工单流转的操作记录
**关键字段**:
- ID: 主键
- SHEET_ID: 工单ID
- LINK_ID: 关联ID
- OPERATE_LINK: 操作环节
- OPERATE_TYPE: 操作类型
- OPERATE_TIME: 操作时间
- CLASS_JSON: JSON格式的类数据

**索引**:
- PRIMARY KEY (ID)
- INDEX idx_sheet_id (SHEET_ID)
- INDEX idx_link_id (LINK_ID)
- INDEX idx_create_time (CREATE_TIME)
- INDEX idx_update_time (UPDATE_TIME)

## 数据类型映射

| Oracle类型 | MySQL类型 | 说明 |
|-----------|----------|------|
| VARCHAR2(n) | VARCHAR(n) | 字符串类型 |
| NUMBER | INT/DECIMAL | 数值类型 |
| DATE | DATETIME | 日期时间 |
| CLOB | TEXT | 大文本 |
| BLOB | BLOB | 二进制数据 |

## 注意事项

### 字符集
- 所有表使用 `utf8mb4` 字符集
- 支持中文、emoji等特殊字符
- 确保MySQL服务器配置了正确的字符集

### 性能优化
如果数据量很大(百万级以上):

1. **导入前优化**:
```sql
SET FOREIGN_KEY_CHECKS=0;
SET UNIQUE_CHECKS=0;
SET AUTOCOMMIT=0;
```

2. **禁用索引**(可选):
```sql
ALTER TABLE table_name DISABLE KEYS;
-- 导入数据
ALTER TABLE table_name ENABLE KEYS;
```

3. **调整MySQL配置**:
```ini
[mysqld]
innodb_buffer_pool_size=4G
innodb_log_file_size=1G
max_allowed_packet=100M
```

### 时区设置
确保MySQL时区设置正确:
```sql
SET GLOBAL time_zone = '+8:00';
```

## 验证数据

导入完成后,运行以下SQL验证:

```sql
-- 查看所有表
SHOW TABLES;

-- 查看记录数
SELECT 
    'MW_ORDER_CIRCULATE_INFO' AS table_name, 
    COUNT(*) AS record_count 
FROM MW_ORDER_CIRCULATE_INFO
UNION ALL
SELECT 'MW_ORDER_WORK', COUNT(*) FROM MW_ORDER_WORK
UNION ALL
SELECT 'MW_ORDER_PUBLIC_INCIDENT', COUNT(*) FROM MW_ORDER_PUBLIC_INCIDENT
UNION ALL
SELECT 'MW_ORDER_CIRCULATE', COUNT(*) FROM MW_ORDER_CIRCULATE;

-- 查看示例数据
SELECT * FROM MW_ORDER_CIRCULATE_INFO LIMIT 5;
SELECT * FROM MW_ORDER_WORK LIMIT 5;
SELECT * FROM MW_ORDER_PUBLIC_INCIDENT LIMIT 5;
SELECT * FROM MW_ORDER_CIRCULATE LIMIT 5;
```

## 常见问题

### Q1: 导入速度慢?
**A**: 
- 增加 innodb_buffer_pool_size
- 禁用外键检查和唯一性检查
- 使用批量插入

### Q2: 中文乱码?
**A**:
- 确保数据库、表、连接都使用utf8mb4
- 检查客户端字符集设置
```sql
SHOW VARIABLES LIKE 'character_set%';
```

### Q3: 日期格式错误?
**A**:
- 确认日期格式为 'YYYY-MM-DD HH:MM:SS'
- 如需微秒精度,使用DATETIME(6)类型

### Q4: 内存不足?
**A**:
- 分批导入数据
- 减少 innodb_buffer_pool_size
- 关闭其他应用程序

## 文件位置

```
/Users/linziwang/PycharmProjects/task-scheduler/
├── mysql_create_tables.sql          # 建表脚本
├── convert_oracle_to_mysql.py       # 数据转换脚本
├── import_to_mysql.sh               # 导入脚本
├── MYSQL_IMPORT_GUIDE.md            # 详细导入指南
└── ORACLE_TO_MYSQL_README.md        # 本文件

/Users/linziwang/Downloads/
├── MW_ORDER_CIRCULATE_INFO.sql      # 原始Oracle数据(源文件)
├── MW_ORDER_WORK.sql                # 原始Oracle数据(源文件)
├── MW_ORDER_PUBLIC_INCIDENT.sql     # 原始Oracle数据(源文件)
├── MW_ORDER_CIRCULATE.sql           # 原始Oracle数据(源文件)
├── MW_ORDER_CIRCULATE_INFO_mysql.sql      # 转换后的MySQL数据
├── MW_ORDER_WORK_mysql.sql              # 转换后的MySQL数据
├── MW_ORDER_PUBLIC_INCIDENT_mysql.sql   # 转换后的MySQL数据
└── MW_ORDER_CIRCULATE_mysql.sql         # 转换后的MySQL数据
```

## 技术支持

如遇到问题:
1. 检查MySQL错误日志
2. 查看 MYSQL_IMPORT_GUIDE.md 中的故障排查章节
3. 确认MySQL版本兼容性(MySQL 5.7+ 或 8.0+)

## 总结

✅ 已完成:
- [x] 生成4个MySQL表的CREATE TABLE语句
- [x] 创建数据转换Python脚本
- [x] 转换4个Oracle SQL文件为MySQL格式(共200条记录)
- [x] 创建自动化导入脚本
- [x] 编写详细文档

📋 下一步:
- [ ] 运行 import_to_mysql.sh 导入数据
- [ ] 验证数据完整性
- [ ] 根据实际需求调整表结构

---
**生成时间**: 2025年  
**工具版本**: Python 3.x, MySQL 5.7+/8.0+
