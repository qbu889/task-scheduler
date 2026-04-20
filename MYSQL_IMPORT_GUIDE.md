# MySQL 建表和数据导入指南

## 概述
本文档说明如何将Oracle SQL文件中的数据导入到MySQL数据库。

## 文件说明
已生成4个MySQL表的CREATE TABLE语句:
1. **MW_ORDER_CIRCULATE_INFO** - 工单流转信息表 (163个字段)
2. **MW_ORDER_WORK** - 工单工作表 (89个字段)
3. **MW_ORDER_PUBLIC_INCIDENT** - 公共事件表 (169个字段)
4. **MW_ORDER_CIRCULATE** - 工单流转表 (25个字段)

## 前置条件
- MySQL服务器已安装并运行
- 有创建数据库和表的权限
- 有数据导入的权限

## 步骤一:创建数据库(可选)
```sql
CREATE DATABASE IF NOT EXISTS monitorwo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE monitorwo;
```

## 步骤二:执行建表脚本

### 方法1:使用MySQL命令行
```bash
mysql -u root -p monitorwo < /Users/linziwang/PycharmProjects/task-scheduler/mysql_create_tables.sql
```

### 方法2:使用MySQL客户端工具
1. 打开MySQL Workbench、Navicat或其他MySQL客户端
2. 连接到MySQL服务器
3. 选择目标数据库
4. 打开 `mysql_create_tables.sql` 文件
5. 执行SQL脚本

## 步骤三:数据转换和导入

由于原始SQL文件是Oracle格式,需要进行以下转换才能导入MySQL:

### Oracle到MySQL的主要差异:

1. **引号处理**:
   - Oracle使用双引号 `"column_name"`
   - MySQL使用反引号 `` `column_name` ``

2. **日期时间格式**:
   - Oracle: `'2025-01-08 09:54:40.000000'`
   - MySQL: `'2025-01-08 09:54:40'` (去掉微秒部分)

3. **NULL值处理**:
   - Oracle: `null` 或 `NULL`
   - MySQL: 相同,但需要确保大小写一致

4. **Schema名称**:
   - Oracle: `"MONITORWO"."MW_ORDER_CIRCULATE_INFO"`
   - MySQL: `MW_ORDER_CIRCULATE_INFO` (去掉schema前缀)

### 数据转换脚本

我为您创建了一个Python脚本来自动转换数据:

```bash
python3 convert_oracle_to_mysql.py
```

或者手动转换每个文件:

#### 使用sed命令批量转换(推荐):

```bash
# 转换 MW_ORDER_CIRCULATE_INFO
sed -E \
  -e 's/"MONITORWO"\."MW_ORDER_CIRCULATE_INFO"/`MW_ORDER_CIRCULATE_INFO`/g' \
  -e 's/"([^"]+)"/`\1`/g' \
  -e "s/'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+'/'\1'/g" \
  /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_INFO.sql \
  > /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_INFO_mysql.sql

# 转换 MW_ORDER_WORK
sed -E \
  -e 's/"MONITORWO"\."MW_ORDER_WORK"/`MW_ORDER_WORK`/g' \
  -e 's/"([^"]+)"/`\1`/g' \
  -e "s/'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+'/'\1'/g" \
  /Users/linziwang/Downloads/MW_ORDER_WORK.sql \
  > /Users/linziwang/Downloads/MW_ORDER_WORK_mysql.sql

# 转换 MW_ORDER_PUBLIC_INCIDENT
sed -E \
  -e 's/"MONITORWO"\."MW_ORDER_PUBLIC_INCIDENT"/`MW_ORDER_PUBLIC_INCIDENT`/g' \
  -e 's/"([^"]+)"/`\1`/g' \
  -e "s/'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+'/'\1'/g" \
  /Users/linziwang/Downloads/MW_ORDER_PUBLIC_INCIDENT.sql \
  > /Users/linziwang/Downloads/MW_ORDER_PUBLIC_INCIDENT_mysql.sql

# 转换 MW_ORDER_CIRCULATE
sed -E \
  -e 's/"MONITORWO"\.\"MW_ORDER_CIRCULATE\"/`MW_ORDER_CIRCULATE`/g' \
  -e 's/"([^"]+)"/`\1`/g' \
  -e "s/'([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+'/'\1'/g" \
  /Users/linziwang/Downloads/MW_ORDER_CIRCULATE.sql \
  > /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_mysql.sql
```

### 导入转换后的数据:

```bash
# 导入各个表的数据
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_INFO_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_WORK_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_PUBLIC_INCIDENT_mysql.sql
mysql -u root -p monitorwo < /Users/linziwang/Downloads/MW_ORDER_CIRCULATE_mysql.sql
```

## 步骤四:验证数据

```sql
-- 检查各表记录数
SELECT COUNT(*) AS circulate_info_count FROM MW_ORDER_CIRCULATE_INFO;
SELECT COUNT(*) AS work_count FROM MW_ORDER_WORK;
SELECT COUNT(*) AS public_incident_count FROM MW_ORDER_PUBLIC_INCIDENT;
SELECT COUNT(*) AS circulate_count FROM MW_ORDER_CIRCULATE;

-- 查看示例数据
SELECT * FROM MW_ORDER_CIRCULATE_INFO LIMIT 5;
SELECT * FROM MW_ORDER_WORK LIMIT 5;
SELECT * FROM MW_ORDER_PUBLIC_INCIDENT LIMIT 5;
SELECT * FROM MW_ORDER_CIRCULATE LIMIT 5;
```

## 注意事项

1. **字符集**: 所有表都使用 `utf8mb4` 字符集,支持中文和emoji
2. **索引**: 已为常用查询字段创建索引(ID, LINK_ID, SHEET_ID, CREATE_TIME等)
3. **数据类型映射**:
   - Oracle VARCHAR2 → MySQL VARCHAR
   - Oracle NUMBER → MySQL INT 或 DECIMAL
   - Oracle DATE → MySQL DATETIME
   - Oracle CLOB → MySQL TEXT
4. **性能优化**: 如果数据量很大,建议:
   - 导入前临时禁用索引: `ALTER TABLE table_name DISABLE KEYS;`
   - 导入后重新启用: `ALTER TABLE table_name ENABLE KEYS;`
   - 调整innodb_buffer_pool_size参数

## 故障排查

### 问题1:导入速度慢
**解决方案**:
- 增加innodb_buffer_pool_size
- 禁用外键检查: `SET FOREIGN_KEY_CHECKS=0;`
- 批量插入而非逐条插入

### 问题2:字符乱码
**解决方案**:
- 确保数据库、表、连接都使用utf8mb4
- 检查客户端字符集: `SHOW VARIABLES LIKE 'character_set%';`

### 问题3:日期格式错误
**解决方案**:
- 确保日期格式为 'YYYY-MM-DD HH:MM:SS'
- 去掉微秒部分或使用DATETIME(6)类型

## 联系支持
如有问题,请检查:
1. MySQL错误日志
2. 数据文件格式是否正确
3. 权限是否足够

---
生成时间: 2025年
文件位置: /Users/linziwang/PycharmProjects/task-scheduler/mysql_create_tables.sql
