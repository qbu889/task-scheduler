# task-scheduler 通用SQL查询与导出功能需求文档

> 本文档面向 AI 智能体开发，定义了 **task-scheduler** 项目中"通用SQL查询并导出为 Excel"功能的完整需求。  
> 核心特性：**SQL语句可配置、多数据源支持、动态时间参数、Web界面管理**，实现灵活的定时数据提取与导出。  
> 所有开发必须遵循项目根目录下的《task-scheduler 项目开发规范（面向AI智能体）》。

---

## 1. 功能概述

### 1.1 业务背景
运维系统中存在大量复杂的数据查询需求，涉及多表关联、条件筛选、字段映射等。业务人员需要定期（每日/每周）执行特定的SQL查询，并将结果导出为 Excel 报表。由于查询逻辑复杂且可能随需求变化，因此要求系统支持**可配置的SQL模板**、**多数据源切换**、**动态时间参数**，避免硬编码。

### 1.2 核心目标
- **SQL可配置**：通过Web界面配置完整的SQL查询语句，支持复杂的多表关联、CASE WHEN、子查询等。
- **多数据源支持**：支持MySQL（开发环境）、达梦数据库（生产环境）等多种数据源，可在配置中指定。
- **动态时间参数**：支持在SQL中使用占位符（如 `:start_time`、`:end_time`），系统自动计算并替换为实际时间值，**支持实时预览计算结果**。
- **定时触发**：支持 Cron 表达式配置，**提供可视化Cron生成器**，自动执行查询任务。
- **导出格式**：生成 Excel `.xlsx` 文件，保留SQL中的列别名作为表头。
- **输出位置**：保存到服务器指定目录（可配置），文件名包含时间戳和任务名称。
- **Web管理界面**：提供可视化界面进行SQL配置、数据源管理、任务调度、手动触发等操作，**采用Claude Design设计规范**。
- **可追溯**：每次执行记录日志（成功/失败、记录数、耗时），支持通过CI报告推送结果至QQ邮箱（524722511@qq.com）。

---

## 2. SQL配置管理

### 2.1 配置存储方式

系统维护一张**SQL任务配置表**，存储在数据库中（MySQL/达梦），支持在线编辑和管理：

| 方式 | 说明 | 优势 |
|------|------|------|
| **数据库表** | 创建 `sql_export_task` 表存储配置 | 支持Web界面管理、版本控制、权限管理 |

### 2.2 配置项定义

每个SQL导出任务包含以下配置项：

| 字段名 | 类型 | 说明 | 示例 |
|--------|------|------|------|
| `task_id` | INT | 任务ID（主键） | `1` |
| `task_name` | VARCHAR(200) | 任务名称 | `泉州遗留库工单日报` |
| `datasource_type` | VARCHAR(50) | 数据源类型 | `mysql` / `dm`（达梦） |
| `datasource_config` | TEXT | 数据源连接配置（JSON格式） | `{"host":"localhost","port":3306,...}` |
| `sql_template` | TEXT | SQL查询模板（支持占位符） | `SELECT ... WHERE CREATE_TIME BETWEEN :start_time AND :end_time` |
| `time_params` | TEXT | 时间参数配置（JSON格式） | `{"start_time":{"type":"fixed","value":"2025-01-01 00:00:00"},"end_time":{"type":"relative","offset_days":-1}}` |
| `cron_expression` | VARCHAR(100) | Cron表达式 | `0 0 2 * * *` |
| `export_path` | VARCHAR(500) | 导出文件路径 | `D:/exports/` |
| `filename_prefix` | VARCHAR(100) | 文件名前缀 | `泉州遗留库工单` |
| `max_rows` | INT | 最大记录数限制 | `100000` |
| `batch_size` | INT | 分页查询大小 | `5000` |
| `is_enabled` | TINYINT | 是否启用（0-否，1-是） | `1` |
| `description` | TEXT | 任务描述 | `每日导出泉州地区遗留库工单数据` |
| `created_at` | DATETIME | 创建时间 | 自动生成 |
| `updated_at` | DATETIME | 更新时间 | 自动更新 |

### 2.3 时间参数配置规则

支持两种时间参数类型，**前端提供实时预览功能**：

#### （1）固定时间（fixed）
```json
{
  "start_time": {
    "type": "fixed",
    "value": "2025-01-01 00:00:00"
  }
}
```

#### （2）相对时间（relative）
```json
{
  "end_time": {
    "type": "relative",
    "offset_days": -1,        // 相对于当前时间的偏移天数（负数表示过去）
    "time_of_day": "23:59:59" // 可选，指定具体时间，默认为 00:00:00
  }
}
```

**示例**：
- 开始时间固定为 `2025-01-01 00:00:00`
- 结束时间为前一天的 `23:59:59`

```json
{
  "start_time": {
    "type": "fixed",
    "value": "2025-01-01 00:00:00"
  },
  "end_time": {
    "type": "relative",
    "offset_days": -1,
    "time_of_day": "23:59:59"
  }
}
```

**前端实时预览**：
- 配置时间参数后，立即显示计算出的实际时间
- 修改偏移天数或时间时，预览自动更新
- 便于用户确认配置是否正确

### 2.4 SQL模板占位符

SQL中使用 `:param_name` 格式的占位符，系统会自动替换为计算后的时间值：

```sql
WHERE A.CREATE_TIME BETWEEN :start_time AND :end_time
```

执行时会被替换为：
```sql
WHERE A.CREATE_TIME BETWEEN '2025-01-01 00:00:00' AND '2026-04-19 23:59:59'
```

---

### 2.5 Cron表达式配置

**前端提供可视化Cron生成器**，支持以下预设模式：

| 模式 | 说明 | 示例 | 生成结果 |
|------|------|------|----------|
| 每N分钟 | 每隔指定分钟执行 | 每2分钟 | `*/2 * * * *` |
| 每小时 | 每小时的第N分钟 | 第30分钟 | `30 * * * *` |
| 每天 | 每天指定时间 | 凌晨2点 | `0 2 * * *` |
| 每周 | 每周几的指定时间 | 周一9点 | `0 9 * * 1` |
| 每月 | 每月几号的指定时间 | 1号凌晨 | `0 0 1 * *` |
| 自定义 | 手动输入Cron表达式 | - | 用户自定义 |

**下次执行时间预览**：
- 配置Cron表达式后，自动计算并显示未来3次执行时间
- 便于用户确认调度计划是否符合预期

**5字段格式说明**：`分 时 日 月 周`
- `*/2 * * * *` - 每2分钟
- `0 2 * * *` - 每天凌晨2点
- `0 9 * * 1` - 每周一上午9点

---

## 3. 数据源配置

### 3.1 支持的数据源类型

| 数据源类型 | 标识符 | 驱动 | 适用环境 |
|-----------|--------|------|----------|
| MySQL | `mysql` | pymysql | 开发环境 |
| 达梦数据库 | `dm` | dmPython | 生产环境 |

### 3.2 数据源配置格式（JSON）

#### MySQL 配置示例
```json
{
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "password": "12345678",
  "database": "task_scheduler_dev",
  "charset": "utf8mb4",
  "connect_timeout": 30
}
```

#### 达梦数据库配置示例
```json
{
  "host": "127.0.0.1",
  "port": 5236,
  "user": "SYSDBA",
  "password": "your_password",
  "database": "TASK_DB",
  "charset": "utf8",
  "connect_timeout": 30,
  "autoCommit": false
}
```

### 3.3 数据源管理

- 支持在Web界面配置多个数据源
- 每个SQL任务可选择使用的数据源
- 数据源密码加密存储（使用Fernet对称加密）
- 支持测试连接功能

---

## 4. 导出功能详细设计

### 4.1 导出流程

```
1. 定时任务触发（或手动触发）
   ↓
2. 从数据库加载任务配置（SQL模板、数据源、时间参数等）
   ↓
3. 根据时间参数配置计算实际时间值
   ↓
4. 替换SQL模板中的占位符（:start_time, :end_time等）
   ↓
5. 使用配置的数据源建立数据库连接
   ↓
6. 执行SQL查询（支持分页，每页batch_size条）
   ↓
7. 将查询结果写入 pandas DataFrame
   ↓
8. 使用 openpyxl 引擎生成 Excel 文件（列名为SQL中的别名）
   ↓
9. 保存文件到配置路径，文件名格式：{filename_prefix}_YYYYMMDD_HHMMSS.xlsx
   ↓
10. 记录执行日志（成功/失败、记录数、文件大小、耗时）
   ↓
11. 若启用邮件通知，发送报告到 524722511@qq.com
```

### 4.2 SQL执行与分页

- **大查询处理**：若查询结果超过 `batch_size`，使用游标分批读取，避免内存溢出
- **参数化查询**：使用 SQLAlchemy 的参数化查询防止 SQL 注入
- **超时控制**：设置查询超时时间（默认300秒）
- **错误处理**：捕获数据库异常、网络异常，记录详细错误信息

### 4.3 Excel生成

- **表头**：直接使用SQL查询结果的列名（即AS别名）
- **数据类型**：自动识别并保持原始数据类型
- **日期格式化**：datetime类型自动格式化为 `YYYY-MM-DD HH:MM:SS`
- **空值处理**：NULL值显示为空单元格
- **大文件分片**：若总记录数 > `max_rows_per_file`（默认50000），自动拆分为多个Excel文件

### 4.4 文件名生成规则

```
{filename_prefix}_{timestamp}.xlsx
```

示例：
- `泉州遗留库工单_20260420_020000.xlsx`
- 若分片：`泉州遗留库工单_20260420_020000_part1.xlsx`

---

## 5. 数据库模型设计

### 5.1 SQL导出任务表（sql_export_task）

```python
# backend/app/models/sql_export_task.py
from app import db
from datetime import datetime
import json

class SqlExportTask(db.Model):
    __tablename__ = 'sql_export_task'
    
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(200), nullable=False, comment='任务名称')
    datasource_type = db.Column(db.String(50), nullable=False, comment='数据源类型：mysql/dm')
    datasource_config = db.Column(db.Text, nullable=False, comment='数据源配置JSON')
    sql_template = db.Column(db.Text, nullable=False, comment='SQL模板')
    time_params = db.Column(db.Text, nullable=False, comment='时间参数配置JSON')
    cron_expression = db.Column(db.String(100), nullable=False, comment='Cron表达式')
    export_path = db.Column(db.String(500), nullable=False, comment='导出路径')
    filename_prefix = db.Column(db.String(100), nullable=False, comment='文件名前缀')
    max_rows = db.Column(db.Integer, default=100000, comment='最大记录数')
    batch_size = db.Column(db.Integer, default=5000, comment='分页大小')
    is_enabled = db.Column(db.SmallInteger, default=1, comment='0-停用 1-启用')
    description = db.Column(db.Text, comment='任务描述')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def get_datasource_config(self):
        """解密并返回数据源配置"""
        from app.utils.crypto import decrypt
        config = json.loads(self.datasource_config)
        if 'password' in config:
            config['password'] = decrypt(config['password'])
        return config
    
    def get_time_params(self):
        """返回时间参数配置"""
        return json.loads(self.time_params)
    
    def to_dict(self):
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'datasource_type': self.datasource_type,
            'sql_template': self.sql_template,
            'cron_expression': self.cron_expression,
            'export_path': self.export_path,
            'filename_prefix': self.filename_prefix,
            'max_rows': self.max_rows,
            'batch_size': self.batch_size,
            'is_enabled': self.is_enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

### 5.2 执行日志表（sql_export_log）

```python
# backend/app/models/sql_export_log.py
from app import db
from datetime import datetime

class SqlExportLog(db.Model):
    __tablename__ = 'sql_export_log'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('sql_export_task.task_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, comment='开始时间')
    end_time = db.Column(db.DateTime, comment='结束时间')
    status = db.Column(db.String(20), nullable=False, comment='success/failed')
    record_count = db.Column(db.Integer, default=0, comment='记录数')
    file_path = db.Column(db.String(500), comment='文件路径')
    file_size = db.Column(db.BigInteger, comment='文件大小（字节）')
    duration_seconds = db.Column(db.Float, comment='耗时（秒）')
    error_message = db.Column(db.Text, comment='错误信息')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    task = db.relationship('SqlExportTask', backref='logs')
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'task_id': self.task_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status,
            'record_count': self.record_count,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

---

## 6. API 接口设计

### 6.1 任务管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sql-export/tasks` | 获取任务列表（支持分页、筛选） |
| GET | `/api/sql-export/tasks/<task_id>` | 获取任务详情 |
| POST | `/api/sql-export/tasks` | 创建新任务 |
| PUT | `/api/sql-export/tasks/<task_id>` | 更新任务配置 |
| DELETE | `/api/sql-export/tasks/<task_id>` | 删除任务 |
| PUT | `/api/sql-export/tasks/<task_id>/enable` | 启用任务 |
| PUT | `/api/sql-export/tasks/<task_id>/disable` | 停用任务 |

### 6.2 执行控制接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sql-export/tasks/<task_id>/trigger` | 手动触发任务执行 |
| GET | `/api/sql-export/logs` | 获取执行日志列表 |
| GET | `/api/sql-export/logs/<log_id>` | 获取日志详情 |
| GET | `/api/sql-export/logs/<log_id>/download` | 下载导出文件 |

### 6.3 数据源管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/sql-export/datasources/test` | 测试数据源连接 |

### 6.4 请求/响应示例

#### 创建任务
```json
POST /api/sql-export/tasks
{
  "task_name": "泉州遗留库工单日报",
  "datasource_type": "dm",
  "datasource_config": {
    "host": "192.168.1.100",
    "port": 5236,
    "user": "SYSDBA",
    "password": "your_password",  // 前端明文传输，后端加密存储
    "database": "MONITORWO",
    "charset": "utf8"
  },
  "sql_template": "SELECT A.sheet_Id AS 工单流水号, A.title AS 工单主题 FROM MW_ORDER_WORK A WHERE A.CREATE_TIME BETWEEN :start_time AND :end_time",
  "time_params": {
    "start_time": {
      "type": "relative",
      "offset_days": -7,
      "time_of_day": "00:00:00"
    },
    "end_time": {
      "type": "relative",
      "offset_days": -1,
      "time_of_day": "23:59:59"
    }
  },
  "cron_expression": "0 2 * * *",
  "export_path": "D:/exports/",
  "filename_prefix": "泉州遗留库工单",
  "max_rows": 100000,
  "batch_size": 5000,
  "is_enabled": 1,
  "description": "每日导出泉州地区遗留库工单数据"
}
```

**注意**：
- `datasource_config.password` 前端以明文传输，后端使用 Fernet 加密后存储
- `time_params` 支持 `fixed` 和 `relative` 两种类型
- `cron_expression` 为 5 字段格式（分 时 日 月 周）

#### 手动触发
```json
POST /api/sql-export/tasks/1/trigger
{
  "override_time_params": {  // 可选，覆盖默认时间参数
    "start_time": "2026-04-01 00:00:00",
    "end_time": "2026-04-19 23:59:59"
  }
}
```

响应：
```json
{
  "success": true,
  "message": "任务已提交执行",
  "log_id": 123
}
```

#### 获取任务列表
```json
GET /api/sql-export/tasks?page=1&page_size=10&is_enabled=1

{
  "success": true,
  "data": [
    {
      "task_id": 1,
      "task_name": "泉州遗留库工单日报",
      "datasource_type": "dm",
      "cron_expression": "0 0 2 * * *",
      "is_enabled": 1,
      "created_at": "2026-04-20T10:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10
}
```

---

## 7. 开发任务分解（面向 AI Agent）

### 7.1 后端模块

#### 7.1.1 数据模型层
- 文件：`backend/app/models/sql_export_task.py`
- 文件：`backend/app/models/sql_export_log.py`
- 功能：定义SQL导出任务和执行日志的数据模型

#### 7.1.2 时间参数计算模块
- 文件：`backend/app/utils/time_calculator.py`
- 功能：
  - `calculate_time_param(param_config)` 根据配置计算实际时间值
  - 支持 fixed 和 relative 两种类型
  - 返回格式化后的时间字符串

#### 7.1.3 SQL执行引擎
- 文件：`backend/app/services/sql_executor.py`
- 功能：
  - `execute_sql(datasource_config, sql_template, time_params)` 执行SQL查询
  - 支持分页查询和大结果集处理
  - 自动替换SQL占位符
  - 返回 pandas DataFrame

#### 7.1.4 Excel导出服务
- 文件：`backend/app/services/excel_exporter.py`
- 功能：
  - `export_to_excel(dataframe, filepath, filename_prefix)` 生成Excel文件
  - 支持大文件分片
  - 自动格式化日期类型

#### 7.1.5 任务管理服务
- 文件：`backend/app/services/sql_export_service.py`
- 功能：
  - `create_task(config)` 创建任务
  - `update_task(task_id, config)` 更新任务
  - `execute_task(task_id, override_params=None)` 执行任务
  - `get_task_list(page, page_size, filters)` 获取任务列表
  - `get_execution_logs(task_id, page, page_size)` 获取执行日志

#### 7.1.6 API路由层
- 文件：`backend/app/api/sql_export.py`
- 功能：实现所有REST API接口

#### 7.1.7 定时任务集成
- 文件：`backend/app/scheduler/job_manager.py`
- 功能：
  - 启动时加载所有启用的SQL导出任务
  - 注册APScheduler定时任务
  - 支持动态添加/删除/更新定时任务

#### 7.1.8 数据源加密工具
- 文件：`backend/app/utils/crypto.py`
- 功能：
  - `encrypt(password)` 加密密码
  - `decrypt(encrypted_password)` 解密密码

### 7.2 前端模块（Vue 3 + Element Plus）

#### 7.2.1 任务管理页面
- 文件：`frontend/src/views/SqlExportTasks.vue`
- 功能：
  - 任务列表展示（表格）
  - 搜索、筛选、分页
  - 新建/编辑/删除任务
  - 启用/停用任务
  - 手动触发执行

#### 7.2.2 任务配置表单
- 文件：`frontend/src/components/SqlExportTaskForm.vue`
- 功能：
  - 任务基本信息输入
  - SQL编辑器（支持语法高亮）
  - 时间参数配置（可视化表单）
  - 数据源配置
  - Cron表达式选择器
  - 表单验证

#### 7.2.3 执行日志页面
- 文件：`frontend/src/views/SqlExportLogs.vue`
- 功能：
  - 日志列表展示
  - 查看详细信息
  - 下载导出文件（若存在）

#### 7.2.4 API封装
- 文件：`frontend/src/api/sqlExport.js`
- 功能：封装所有后端API调用

### 7.3 测试要求

- **单元测试**：
  - 测试时间参数计算（fixed、relative各种场景）
  - 测试SQL占位符替换
  - 测试Excel生成（表头、数据类型、分片）
  - 测试密码加密/解密
- **集成测试**：
  - 使用MySQL测试完整执行流程
  - 测试多数据源切换
  - 测试大查询分页
  - 测试定时任务触发
- **覆盖率要求**：核心模块 ≥ 85%

### 7.4 部署注意事项

- 生产环境（达梦）需提前安装 `dmPython` 和 `sqlalchemy-dm`
- 导出目录需有写入权限，建议使用绝对路径
- 数据源密码使用Fernet加密存储，密钥保存在环境变量中
- SQL执行设置超时时间，避免长时间占用数据库连接
- 定期清理历史执行日志，避免数据库膨胀

---

## 8. 示例SQL配置

### 8.1 泉州遗留库工单日报

**任务名称**：泉州遗留库工单日报  
**数据源**：达梦数据库  
**Cron表达式**：`0 0 2 * * *`（每天凌晨2点执行）  
**时间参数**：
```json
{
  "start_time": {
    "type": "fixed",
    "value": "2025-01-01 00:00:00"
  },
  "end_time": {
    "type": "relative",
    "offset_days": -1,
    "time_of_day": "23:59:59"
  }
}
```

**SQL模板**：
```sql
SELECT
    A.sheet_Id AS 工单流水号,
    A.title AS 工单主题,
    A.main_City AS 地市,
    A.main_County AS 区县,
    CASE c.provincelevel
        WHEN '1' THEN '一级'
        WHEN '2' THEN '二级'
        ELSE c.provincelevel
    END AS 省内派单级别,
    CASE A.status
        WHEN 'ACCEPTING' THEN '已受理'
        WHEN 'ARCHIVED' THEN '已归档'
        WHEN 'IN_PROGRESS' THEN '处理中'
        ELSE A.status
    END AS 工单状态,
    A.send_Time AS 派单时间,
    A.end_Time AS 归档时间,
    c.event_Id AS 事件编码,
    c.event_Name AS 事件名称,
    c.event_Happen_Time AS 事件发生时间,
    legacy_apply.create_Time AS 最后一次入遗留库申请时间,
    legacy_approve.create_Time AS 最后一次入遗留库审批通过时间
FROM MONITORWO.MW_ORDER_WORK A
LEFT JOIN MONITORWO.MW_ORDER_PUBLIC_INCIDENT C
    ON A.EVENT_NUMBER = C.EVENT_NUMBER
LEFT JOIN (
    SELECT sheet_id, create_Time,
        ROW_NUMBER() OVER (PARTITION BY sheet_id ORDER BY CREATE_TIME DESC) as rn
    FROM MONITORWO.MW_ORDER_CIRCULATE
    WHERE OPERATE_TYPE IN ('T1_LEGACY_APPLICATION','T2_LEGACY_APPLICATION')
) legacy_apply
    ON A.sheet_id = legacy_apply.sheet_id AND legacy_apply.rn = 1
LEFT JOIN (
    SELECT sheet_id, create_Time,
        ROW_NUMBER() OVER (PARTITION BY sheet_id ORDER BY CREATE_TIME DESC) as rn
    FROM MONITORWO.MW_ORDER_CIRCULATE
    WHERE OPERATE_TYPE IN ('T1_LEGACY_APPROVED','T2_LEGACY_APPROVED')
) legacy_approve
    ON A.sheet_id = legacy_approve.sheet_id AND legacy_approve.rn = 1
WHERE A.EVENT_NUMBER IS NOT NULL
  AND A.STATUS NOT IN ('SHIELD', 'EXCEPTION', 'VOIDED', 'DRAFT', 'SUSPENDED')
  AND A.ORDER_TYPE = 'LEGACY_ORDER'
  AND A.CREATE_TIME BETWEEN :start_time AND :end_time
  AND A.MAIN_CITY = '泉州市'
ORDER BY A.SEND_TIME DESC
```

**导出路径**：`D:/exports/`  
**文件名前缀**：`泉州遗留库工单`  
**最大记录数**：100000  
**分页大小**：5000

---

## 9. 文档输出

开发完成后，需要更新 `doc/` 目录下的文档：

- `doc/SQL导出功能使用说明.md`：包含如何配置SQL任务、时间参数说明、手动触发API等用户手册
- `doc/SQL导出功能部署指南.md`：包含数据库初始化脚本、依赖安装、环境变量配置
- `doc/常见问题排查.md`：补充SQL执行失败、数据源连接问题等排查方法

---

## 10. 版本记录

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-04-20 | 初始版本（基于固定字段映射） | AI Agent |
| v2.0 | 2026-04-20 | **重大重构**：改为通用SQL查询导出系统，支持可配置SQL、多数据源、动态时间参数、Web界面管理 | AI Agent |
| v2.1 | 2026-04-21 | **前端功能增强**：<br>- 添加 Cron 表达式可视化生成器<br>- 添加时间参数实时预览<br>- 添加下次执行时间预览<br>- 采用 Claude Design 设计规范<br>- 修复 Flask debug 模式重复初始化问题<br>- 实现达梦驱动延迟加载机制<br>- 调整开发环境端口为 5001 | AI Agent |

---

**本需求文档已对齐《task-scheduler 项目开发规范》，AI 智能体可据此进行编码实现。所有SQL查询均从配置中动态获取，支持多数据源切换和动态时间参数，无需硬编码。**