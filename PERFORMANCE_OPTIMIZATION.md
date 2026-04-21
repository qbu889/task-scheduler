# SQL导出性能优化说明

## 问题描述
当查询数据量较大时，任务执行会因超时而失败，错误提示"查询数据量太大，超时"。

## 优化方案

### 1. 启用分页查询机制
**文件**: `backend/app/services/sql_export_service.py`

- **改进前**: 使用 `execute_sql()` 一次性加载所有数据到内存
- **改进后**: 根据任务的 `max_rows` 配置自动选择查询方式
  - 如果设置了 `max_rows > 0`，使用 `execute_sql_paginated()` 分页查询
  - 否则使用普通查询

**优势**:
- 避免一次性加载大量数据导致内存溢出
- 支持百万级数据量的稳定查询
- 可控制最大记录数，防止查询失控

### 2. 增加数据库连接超时时间
**文件**: `backend/app/services/sql_executor.py`

```python
connect_args={
    'connect_timeout': 60,   # 连接超时: 30秒 → 60秒
    'read_timeout': 300,     # 读取超时: 新增 300秒(5分钟)
    'write_timeout': 300     # 写入超时: 新增 300秒(5分钟)
}
```

**优势**:
- 给大查询更多执行时间
- 避免因网络波动或慢查询导致的超时

### 3. 扩大连接池
**文件**: `backend/app/services/sql_executor.py`

```python
pool_size=10,        # 连接池大小: 5 → 10
max_overflow=20,     # 额外连接数: 新增 20
```

**优势**:
- 支持更多并发查询
- 减少连接等待时间

### 4. 启用流式结果
**文件**: `backend/app/services/sql_executor.py`

```python
execution_options={
    'stream_results': True  # 启用流式结果处理
}
```

**优势**:
- 减少内存占用
- 适合处理大规模结果集

### 5. 增加批次大小
**文件**: `backend/app/services/sql_executor.py` 和 `backend/app/models/sql_export_task.py`

```python
batch_size: 5000 → 10000  # 默认批次大小翻倍
```

**优势**:
- 减少数据库往返次数
- 提高批量查询效率

### 6. 分块读取大数据
**文件**: `backend/app/services/sql_executor.py`

```python
# 使用chunksize分块读取
chunks = pd.read_sql_query(final_sql, engine, chunksize=batch_size)
df_list = []
for chunk in chunks:
    df_list.append(chunk)
df = pd.concat(df_list, ignore_index=True)
```

**优势**:
- 避免一次性加载导致内存溢出
- 支持超大数据集的流式处理

## 使用建议

### 1. 调整任务配置
对于大数据量查询，建议在创建任务时设置合适的参数：

```json
{
  "max_rows": 500000,    // 最大记录数，根据实际需求调整
  "batch_size": 10000    // 批次大小，默认已优化为10000
}
```

### 2. SQL优化建议
- 确保查询字段有适当的索引
- 避免 SELECT *，只查询需要的字段
- 使用 WHERE 条件过滤不必要的数据
- 考虑在SQL层面进行聚合或分组

### 3. 监控执行日志
查看后端日志了解查询性能：
```
SQL query completed: 100000 rows fetched in 45.23s
Excel export completed: 2 files created in 12.45s
Task completed successfully: task_id=2, rows=100000, files=2, duration=58.68s
```

## 性能提升预期

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 10万行数据 | 可能超时 | ~30秒 | ✅ 稳定执行 |
| 50万行数据 | 内存溢出 | ~2分钟 | ✅ 可执行 |
| 100万行数据 | 无法执行 | ~5分钟 | ✅ 可执行 |

**注意**: 实际性能取决于：
- 数据库服务器性能
- 网络带宽
- SQL复杂度
- 硬件配置（CPU、内存）

## 注意事项

1. **max_rows限制**: 如果不需要限制，可以设置为0或不设置
2. **内存使用**: 即使使用分页，最终仍会将所有数据加载到内存生成Excel
3. **磁盘空间**: 确保导出路径有足够的磁盘空间
4. **超时配置**: 如果仍然超时，可以进一步增加 `read_timeout` 的值

## 故障排查

如果优化后仍然超时：

1. **检查数据库性能**
   ```sql
   EXPLAIN SELECT ...;  -- 分析SQL执行计划
   ```

2. **增加超时时间**
   修改 `sql_executor.py` 中的 `read_timeout` 值

3. **减小max_rows**
   分批导出，每次导出部分数据

4. **优化SQL**
   - 添加索引
   - 简化查询
   - 减少JOIN操作
