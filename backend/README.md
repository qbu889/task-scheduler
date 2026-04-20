# task-scheduler 后端

通用SQL查询与导出系统 - Flask后端

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，修改数据库配置等
```

### 3. 初始化数据库

```bash
# 使用MySQL客户端执行初始化脚本
mysql -u root -p < ../scripts/init_db.sql
```

### 4. 启动应用

```bash
python run.py
```

应用将在 http://0.0.0.0:5000 启动

## 项目结构

```
backend/
├── app/
│   ├── __init__.py          # Flask应用工厂
│   ├── api/                  # API路由
│   │   └── sql_export.py    # SQL导出API
│   ├── models/              # 数据模型
│   │   ├── sql_export_task.py
│   │   └── sql_export_log.py
│   ├── services/            # 业务服务
│   │   ├── sql_executor.py      # SQL执行引擎
│   │   ├── excel_exporter.py    # Excel导出服务
│   │   └── sql_export_service.py # 任务管理服务
│   ├── scheduler/           # 定时任务
│   │   └── job_manager.py   # 任务调度器
│   └── utils/               # 工具函数
│       ├── time_calculator.py  # 时间计算
│       └── crypto.py           # 加密解密
├── tests/                   # 测试代码
├── config.py               # 配置文件
├── run.py                  # 启动入口
└── requirements.txt        # 依赖清单
```

## API接口

### 任务管理

- `GET /api/sql-export/tasks` - 获取任务列表
- `POST /api/sql-export/tasks` - 创建任务
- `GET /api/sql-export/tasks/<id>` - 获取任务详情
- `PUT /api/sql-export/tasks/<id>` - 更新任务
- `DELETE /api/sql-export/tasks/<id>` - 删除任务
- `PUT /api/sql-export/tasks/<id>/enable` - 启用任务
- `PUT /api/sql-export/tasks/<id>/disable` - 停用任务

### 执行控制

- `POST /api/sql-export/tasks/<id>/trigger` - 手动触发执行
- `GET /api/sql-export/logs` - 获取执行日志

## 创建任务示例

```bash
curl -X POST http://localhost:5000/api/sql-export/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "测试任务",
    "datasource_type": "mysql",
    "datasource_config": {
      "host": "127.0.0.1",
      "port": 3306,
      "user": "root",
      "password": "12345678",
      "database": "task_scheduler_dev",
      "charset": "utf8mb4"
    },
    "sql_template": "SELECT * FROM your_table WHERE CREATE_TIME BETWEEN :start_time AND :end_time",
    "time_params": {
      "start_time": {"type": "fixed", "value": "2025-01-01 00:00:00"},
      "end_time": {"type": "relative", "offset_days": -1, "time_of_day": "23:59:59"}
    },
    "cron_expression": "0 0 2 * * *",
    "export_path": "./exports/",
    "filename_prefix": "测试导出",
    "max_rows": 100000,
    "batch_size": 5000,
    "is_enabled": 1,
    "description": "测试任务描述"
  }'
```

## 运行测试

```bash
cd backend
pytest tests/unit -v
```

## 注意事项

1. **密码加密**：数据源密码会自动加密存储，无需手动处理
2. **时间参数**：支持固定时间（fixed）和相对时间（relative）两种类型
3. **SQL占位符**：使用 `:param_name` 格式，系统会自动替换
4. **大文件分片**：超过50000行自动分片为多个Excel文件
5. **定时任务**：启用后会自动注册到APScheduler，按Cron表达式执行

## 开发环境

- Python 3.10+
- MySQL 5.7+（开发）
- 达梦DM8（生产）

## 许可证

MIT
