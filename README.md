# task-scheduler 通用SQL查询与导出系统

## 项目简介

这是一个部署于Windows Server上的远程定时任务调度系统，支持通过Web界面配置SQL查询任务，自动定时执行并将结果导出为Excel文件。

### 核心特性

✅ **SQL完全可配置** - 支持复杂的多表关联、CASE WHEN、子查询等  
✅ **多数据源支持** - MySQL（开发）、达梦数据库（生产）可切换  
✅ **动态时间参数** - 支持固定时间和相对时间计算  
✅ **Web管理界面** - 可视化配置SQL任务、数据源、查看日志  
✅ **定时任务调度** - 基于APScheduler，支持Cron表达式  
✅ **大文件处理** - 自动分页查询和Excel分片导出  
✅ **密码加密存储** - 使用Fernet对称加密保护敏感信息  
✅ **完整日志记录** - 每次执行记录详细日志，便于追溯  

## 技术栈

### 后端
- **框架**: Flask 3.0 + Flask-SQLAlchemy
- **数据库**: MySQL（开发）/ 达梦DM8（生产）
- **定时任务**: APScheduler 3.10
- **数据处理**: Pandas 2.1
- **Excel生成**: openpyxl 3.1
- **加密**: cryptography 41.0

### 前端（待开发）
- Vue 3 + Element Plus
- Vite构建工具

## 快速开始

### 方式一：使用启动脚本（推荐）

#### macOS / Linux

```bash
# 开发环境启动（自动安装依赖、初始化数据库、启动服务）
cd scripts
./start_dev.sh

# 生产环境启动（需要先设置环境变量）
export DM_HOST=192.168.1.100
export DM_USER=SYSDBA
export DM_PASSWORD=your_password
export DM_DATABASE=TASK_DB
./start_prod.sh
```

#### Windows

```batch
REM 开发环境启动
scripts\start_dev.bat

REM 生产环境启动（需要先设置环境变量）
set DM_HOST=192.168.1.100
set DM_USER=SYSDBA
set DM_PASSWORD=your_password
set DM_DATABASE=TASK_DB
scripts\start_prod.bat
```

**详细说明请参考**: [scripts/README.md](scripts/README.md)

---

### 方式二：手动启动

#### 1. 环境准备

```bash
# 确保已安装 Python 3.10+、Node.js 16+ 和 MySQL 5.7+
python --version
node --version
mysql --version
```

#### 2. 克隆项目

```bash
cd /Users/linziwang/PycharmProjects/task-scheduler
```

#### 3. 初始化数据库

```bash
# 执行数据库初始化脚本
mysql -u root -p < scripts/init_db.sql
```

#### 4. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

访问 http://localhost:5001 查看API服务

#### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000 使用Web界面

## 项目结构

```
task-scheduler/
├── backend/                     # Flask后端
│   ├── app/
│   │   ├── api/                # API路由层
│   │   ├── models/             # 数据模型
│   │   ├── services/           # 业务服务层
│   │   ├── scheduler/          # 定时任务调度
│   │   └── utils/              # 工具函数
│   ├── tests/                  # 测试代码
│   ├── config.py              # 配置文件
│   ├── run.py                 # 启动入口
│   └── requirements.txt       # 依赖清单
├── frontend/                   # Vue前端
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── scripts/                    # 辅助脚本
│   ├── README.md              # 启动脚本使用说明
│   ├── start_dev.sh           # 开发环境启动 (macOS/Linux)
│   ├── start_dev.bat          # 开发环境启动 (Windows)
│   ├── start_prod.sh          # 生产环境启动 (macOS/Linux)
│   ├── start_prod.bat         # 生产环境启动 (Windows)
│   └── init_db.sql            # 数据库初始化脚本
├── doc/                        # 文档目录
│   ├── need.md                # 开发规范
│   └── task-scheduler/        # 需求文档
│       └── task-scheduler.md
└── README.md                   # 项目说明
```

## API文档

详见 `backend/README.md`

### 主要接口

- **任务管理**: CRUD操作、启用/停用
- **执行控制**: 手动触发、查看日志
- **数据源管理**: 测试连接（待实现）

## 使用示例

### 创建导出任务

```json
POST /api/sql-export/tasks
{
  "task_name": "泉州遗留库工单日报",
  "datasource_type": "mysql",
  "datasource_config": {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12345678",
    "database": "task_scheduler_dev"
  },
  "sql_template": "SELECT * FROM orders WHERE CREATE_TIME BETWEEN :start_time AND :end_time",
  "time_params": {
    "start_time": {"type": "fixed", "value": "2025-01-01 00:00:00"},
    "end_time": {"type": "relative", "offset_days": -1, "time_of_day": "23:59:59"}
  },
  "cron_expression": "0 0 2 * * *",
  "export_path": "./exports/",
  "filename_prefix": "订单日报"
}
```

### 手动触发执行

```json
POST /api/sql-export/tasks/1/trigger
```

## 开发规范

严格遵守 `doc/need.md` 中的开发规范：

- 代码风格：PEP 8（Python）、Vue Style Guide
- Git提交：Conventional Commits
- 测试覆盖：核心模块 ≥ 85%
- 分支策略：Git Flow

## 环境配置

项目提供了环境配置文件模板，位于各模块根目录：

### 后端配置
- `backend/.env.development` - 开发环境（MySQL + 调试模式）
- `backend/.env.production` - 生产环境（达梦数据库 + 关闭调试）

### 前端配置
- `frontend/.env.development` - 开发环境（API代理到localhost:5001）
- `frontend/.env.production` - 生产环境（API使用相对路径）

**注意**: `.env.*` 文件包含敏感信息，不要提交到版本控制系统。

详见 [scripts/README.md](scripts/README.md) 中的环境配置章节。

## 测试

```bash
cd backend
pytest tests/unit -v --cov=app --cov-report=html
```

## 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否启动
- 确认.env中的数据库配置正确
- 验证用户名密码

### 2. 定时任务不执行
- 检查任务的is_enabled是否为1
- 验证Cron表达式格式
- 查看应用日志

### 3. Excel导出为空
- 检查SQL查询是否有结果
- 验证时间参数配置
- 查看执行日志中的错误信息

## 后续开发计划

- [ ] 前端Vue界面开发
- [ ] 数据源管理界面
- [ ] SQL编辑器（语法高亮）
- [ ] Cron表达式可视化选择器
- [ ] 邮件通知功能
- [ ] 文件下载接口
- [ ] 权限管理
- [ ] 更多单元测试

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队。
