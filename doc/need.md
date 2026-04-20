## task-scheduler 项目开发规范（面向AI智能体）

> 本文档旨在规范 **task-scheduler** 项目的开发流程、代码风格、测试策略与协作方式，确保在多人、多AI智能体协作的环境下，项目能够高效、稳定地推进。所有开发者（包括AI智能体）必须严格遵守本规范。

---

## 📌 1. 项目概述

**项目名称**：task-scheduler  
**核心功能**：一个部署于Windows Server上的远程定时任务调度系统。系统通过配置定时规则，在指定的Windows服务器上远程执行预设任务。  
**技术栈**：
- **后端**：Python 3.10 + Flask
- **前端**：Vue 3 + Element Plus
- **数据库**：MySQL（开发环境）/ 达梦数据库DM8（生产环境）
- **定时任务**：APScheduler
- **通信协议**：RESTful API
- **部署环境**：Windows Server（离线环境，需提前准备所有依赖包）
- **测试框架**：pytest（单元测试、接口测试）、Jest/Cypress（前端自动化测试）
- **覆盖率工具**：pytest-cov
- **CI/CD**：Git Hooks / GitHub Actions（触发自动化测试，生成报告并通过QQ邮箱发送）

---

## 📌 2. 数据库连接规范

### 2.1 环境区分

项目采用**双数据库策略**：
- **开发环境**：使用 **MySQL** 进行本地开发，便于快速迭代和调试
- **生产环境**：使用 **达梦数据库（DM8）**，部署于Windows Server离线环境

### 2.2 开发环境 - MySQL配置

在Flask应用中使用 **Flask-SQLAlchemy** 连接MySQL数据库，配置示例：

```python
# config.py
import os

class DevelopmentConfig:
    # MySQL数据库连接URI格式：mysql+pymysql://用户名:密码@主机:端口/数据库名?charset=utf8mb4
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '12345678')
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'task_scheduler_dev')
    
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 30,      # 连接超时30秒
        }
    }
```

**依赖安装**：
```bash
pip install pymysql
pip install sqlalchemy==2.0.30
pip install flask-sqlalchemy
```

### 2.3 生产环境 - 达梦数据库配置

达梦数据库需通过 **dmPython** 驱动和 **sqlalchemy-dm** 方言包进行连接，具体规范如下：

| 组件 | 版本要求 | 来源 | 安装方式 |
|------|---------|------|---------|
| dmPython | 2.5.5 | 达梦安装目录 `drivers/python/dmPython` | 离线编译安装 |
| sqlalchemy-dm | 与SQLAlchemy兼容 | 达梦安装目录 `drivers/python/sqlalchemy` | 离线编译安装 |
| SQLAlchemy | 2.0.30 | PyPI | 离线whl安装 |

> **重要**：`dmPython` 和 `sqlalchemy-dm` 均为**离线部署**，需提前下载并放入 `packages/` 目录。

在Flask应用中使用 **Flask-SQLAlchemy** 连接达梦数据库，配置示例：

```python
# config.py
import os

class ProductionConfig:
    # 达梦数据库连接URI格式：dm+dmPython://用户名:密码@主机:端口/数据库名?charset=utf8
    DM_USER = os.getenv('DM_USER', 'SYSDBA')
    DM_PASSWORD = os.getenv('DM_PASSWORD', 'your_password')
    DM_HOST = os.getenv('DM_HOST', '127.0.0.1')
    DM_PORT = os.getenv('DM_PORT', '5236')
    DM_DATABASE = os.getenv('DM_DATABASE', 'TASK_DB')
    
    SQLALCHEMY_DATABASE_URI = (
        f'dm+dmPython://{DM_USER}:{DM_PASSWORD}@{DM_HOST}:{DM_PORT}/{DM_DATABASE}?charset=utf8'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'connect_args': {
            'connect_timeout': 30,      # 连接超时30秒
            'autoCommit': False         # 默认关闭自动提交
        }
    }
```

### 2.4 连接池与错误处理

| 场景 | 配置/处理方式 |
|------|-------------|
| 长连接断开 | `pool_pre_ping=True` 自动检测连接有效性 |
| 连接泄漏 | 设置 `pool_recycle=3600`（1小时回收） |
| 连接超时 | `connect_timeout=30` |
| 网络异常 | 使用重试装饰器（最多3次，指数退避） |
| 事务管理 | 显式使用 `session.commit()` 和 `session.rollback()` |

### 2.5 dmPython 原生连接示例（生产环境兜底方案）

当 SQLAlchemy 出现兼容性问题时，可使用 dmPython 原生连接：

```python
import dmPython

def get_dm_connection():
    conn = dmPython.connect(
        user='SYSDBA',
        password='your_password',
        server='127.0.0.1',
        port=5236,
        database='TASK_DB',
        autoCommit=False,
        connect_timeout=30
    )
    return conn
```

### 2.6 批量插入性能优化

| 数据量 | 推荐方式 | 预估耗时（4万条） |
|-------|---------|---------------|
| < 1000条 | `session.bulk_save_objects()` | < 1秒 |
| 1000-10000条 | `executemany()` | < 3秒 |
| > 10000条 | 分批 `executemany()`（每批2000条）| < 8秒 |

---

## 📌 3. 开发规范

### 3.1 代码风格

- **Python**：遵循 [PEP 8](https://peps.python.org/pep-0008/)，使用 `black` 格式化，`flake8` 检查
- **Vue**：遵循 [Vue Style Guide](https://vuejs.org/style-guide/)，使用 `ESLint` + `Prettier`
- **行宽限制**：Python 88字符，Vue 100字符
- **命名规范**：
  - 类名：`PascalCase`（例：`TaskScheduler`）
  - 函数/变量：`snake_case`（例：`get_task_list`）
  - 常量：`UPPER_SNAKE_CASE`（例：`MAX_RETRY_COUNT`）
  - Vue组件：`PascalCase`（例：`TaskCard.vue`）

### 3.2 UI设计规范

#### 3.2.1 设计风格定位

本项目前端界面严格遵循 **Claude (Anthropic) 设计风格**，核心理念是「温暖的文学沙龙」而非「冷峻的科技产品」。设计语言强调人文温度、编辑级排版和有机视觉元素。

**核心特征**：
- 暖色调羊皮纸画布（`#f5f4ed`）营造纸质阅读感
- Anthropic Serif 衬线字体用于标题，Sans 无衬线用于UI
- 赤陶色品牌主色（`#c96442`）——温暖、质朴、刻意去科技感
-  exclusively 暖色调中性色 —— 所有灰色都带有黄棕底色
- 有机手绘风格插图替代传统科技图标
- 杂志级排版节奏， generous section spacing

详细设计规范参见：[doc/通用文档/ClaudeDESIGN.md](通用文档/ClaudeDESIGN.md)

#### 3.2.2 色彩系统

**主色调**：
- 页面背景（Parchment）：`#f5f4ed` — 暖奶油色，情感基础
- 卡片表面（Ivory）：`#faf9f5` — 最浅表面，微妙分层
- 主要文字（Near Black）：`#141413` — 暖近黑色，比纯黑柔和
- 次要文字（Olive Gray）：`#5e5d59` — 暖中灰
- 品牌CTA（Terracotta）：`#c96442` — 赤陶色，仅用于主要按钮

**辅助色**：
- 边框奶油色（Border Cream）：`#f0eee6` — 极淡暖边框
- 深色表面（Dark Surface）：`#30302e` — 暗主题容器
- 错误深红（Error Crimson）：`#b53333` — 严肃但不惊悚
- 焦点蓝（Focus Blue）：`#3898ec` — 唯一冷色，仅用于输入框焦点

**禁止使用**：
- ❌ 冷蓝灰色系（整个调色板 exclusively 暖色调）
- ❌ 纯白色（`#ffffff`）作为页面背景
- ❌ 饱和度过高的颜色（除赤陶色外保持 muted）

#### 3.2.3 字体层级

**字体家族**：
- 标题：`Georgia, 'Times New Roman', serif`（Anthropic Serif 替代品）
- 正文/UI：`'Inter', -apple-system, BlinkMacSystemFont, sans-serif`（Anthropic Sans 替代品）
- 代码：`'JetBrains Mono', 'Fira Code', monospace`（Anthropic Mono 替代品）

**字号与行高**：
| 角色 | 字号 | 字重 | 行高 | 用途 |
|------|------|------|------|------|
| Display/Hero | 64px (4rem) | 500 | 1.10 | 最大冲击，书籍标题感 |
| Section Heading | 52px (3.25rem) | 500 | 1.20 | 功能区锚点 |
| Sub-heading | 32px (2rem) | 500 | 1.10 | 卡片标题 |
| Body Large | 20px (1.25rem) | 400 | 1.60 | 介绍段落 |
| Body Standard | 16px (1rem) | 400 | 1.60 | 标准正文 |
| Caption | 14px (0.88rem) | 400 | 1.43 | 元数据、描述 |

**核心原则**：
- 衬线字体用于权威感（标题），无衬线用于功能性（UI）
- 标题统一使用字重500，不粗不细，保持一致「声音」
- 正文字高1.60，显著宽松于典型科技网站（1.4-1.5），接近书籍阅读体验
- 标题行高1.10-1.30，紧凑但不拥挤

#### 3.2.4 组件样式

**按钮**：
```css
/* 次要按钮（Warm Sand） */
.btn-secondary {
  background: #e8e6dc;
  color: #4d4c48;
  padding: 8px 16px 8px 12px;
  border-radius: 8px;
  box-shadow: 0px 0px 0px 0px #e8e6dc, 0px 0px 0px 1px #d1cfc5;
}

/* 主要CTA按钮（Terracotta） */
.btn-primary {
  background: #c96442;
  color: #faf9f5;
  padding: 8px 16px 8px 12px;
  border-radius: 12px;
  box-shadow: 0px 0px 0px 0px #c96442, 0px 0px 0px 1px #c96442;
}

/* 深色按钮 */
.btn-dark {
  background: #30302e;
  color: #faf9f5;
  padding: 8px 16px 8px 12px;
  border-radius: 8px;
}
```

**卡片与容器**：
```css
.card {
  background: #faf9f5;  /* Ivory */
  border: 1px solid #f0eee6;  /* Border Cream */
  border-radius: 8px;  /* comfortably rounded */
  box-shadow: rgba(0, 0, 0, 0.05) 0px 4px 24px;  /* whisper shadow */
  padding: 24px 32px;
}

.card-featured {
  border-radius: 16px;  /* generously rounded */
}
```

**输入框**：
```css
.input-field {
  padding: 1.6px 12px;
  border: 1px solid #f0eee6;
  border-radius: 12px;
  color: #141413;
}

.input-field:focus {
  outline: none;
  border-color: #3898ec;  /* Focus Blue - 唯一冷色时刻 */
  box-shadow: 0 0 0 3px rgba(56, 152, 236, 0.1);
}
```

#### 3.2.5 布局原则

**间距系统**：
- 基础单位：8px
- 刻度：3px, 4px, 6px, 8px, 10px, 12px, 16px, 20px, 24px, 30px
- 卡片内边距：24-32px
- 区块垂直间距：80-120px（generous，杂志级留白）

**圆角刻度**：
- 舒适圆角（8px）：标准按钮、卡片
- 慷慨圆角（12px）：主要按钮、输入框
- 非常圆角（16px）：特色容器、视频播放器
- 最大圆角（32px）：Hero容器、嵌入式媒体

**深度与阴影**：
- Level 0（平面）：无阴影无边框 — 羊皮纸背景
- Level 1（包含）：`1px solid #f0eee6` — 标准卡片
- Level 2（环影）：`0px 0px 0px 1px` 环状阴影 — 交互状态
- Level 3（轻语）：`rgba(0,0,0,0.05) 0px 4px 24px` — 悬浮内容

**核心理念**：通过暖色调环状阴影而非传统投影传达深度，`0px 0px 0px 1px` 模式创造类似边框的光晕效果。

#### 3.2.6 响应式行为

**断点**：
| 名称 | 宽度 | 关键变化 |
|------|------|----------|
| Small Mobile | <479px | 最小布局，全部堆叠 |
| Mobile | 479-640px | 单列，汉堡菜单 |
| Tablet | 768-991px | 2列网格开始 |
| Desktop | 992px+ | 完整多列布局，最大Hero字体（64px） |

**折叠策略**：
- Hero文字：64px → 36px → ~25px 渐进缩放
- 功能区块：多列 → 堆叠单列
- 导航：完整横向 → 汉堡菜单
- 区块padding：成比例减少但保持编辑级节奏

#### 3.2.7 Do's and Don'ts

**必须做**：
- ✅ 使用 Parchment (`#f5f4ed`) 作为主要浅色背景
- ✅ 标题使用 Georgia 字重500，保持一致性
- ✅ Terracotta (`#c96442`) 仅用于主要CTA和最高信号品牌时刻
- ✅ 所有中性色保持暖色调 — 每个灰色都有黄棕底色
- ✅ 使用环状阴影 (`0px 0px 0px 1px`) 替代投影用于交互状态
- ✅ 保持编辑级衬线/无衬线层级 — 衬线用于内容标题，无衬线用于UI
- ✅ 使用 generous 正文字高（1.60）营造文学阅读体验
- ✅ 应用 generous 圆角（12-32px）营造柔软亲和感

**禁止做**：
- ❌ 使用冷蓝灰色系 — 调色板 exclusively 暖色调
- ❌ 对衬线字体使用粗体（700+）— 字重500是上限
- ❌ 引入超出Terracotta的饱和色 — 调色板刻意 muted
- ❌ 在按钮或卡片上使用锐角（<6px圆角）— 柔软性是核心身份
- ❌ 应用重投影 — 深度来自环状阴影和背景色切换
- ❌ 使用纯白（`#ffffff`）作为页面背景 — Parchment 或 Ivory 始终更温暖
- ❌ 使用几何/科技风格插图 — 插图应有机且手绘感
- ❌ 将正文字高降至1.40以下 — generous 间距支持编辑级个性

### 3.3 注释与文档

| 类型 | 要求 |
|------|------|
| **模块注释** | 每个 `.py` 文件顶部描述模块用途 |
| **函数注释** | 使用 Google 风格 docstring，包含参数、返回值、异常说明 |
| **复杂逻辑** | 必须添加行内注释解释意图 |
| **API注释** | 使用 `@bp.route` 装饰器，配合 OpenAPI/Swagger 自动生成文档 |
| **前端组件** | 每个 `.vue` 文件顶部说明组件用途 |

### 3.4 日志规范

#### 3.4.1 日志配置要求

**核心原则**：日志系统必须可配置、分级输出、便于问题排查和性能分析。

**配置方式**：
```python
# config.py
import logging
import os

class BaseConfig:
    # 日志级别（可通过环境变量覆盖）
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 日志格式
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    
    # 日志文件路径
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # 日志文件大小限制（MB）
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10 * 1024 * 1024))  # 默认10MB
    
    # 日志文件备份数量
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
```

**日志级别定义**：
- `DEBUG`：调试信息，仅开发环境使用
- `INFO`：关键业务流程节点（任务创建、执行开始/结束等）
- `WARNING`：潜在问题但不影响运行（查询无数据、配置缺失等）
- `ERROR`：错误但程序可继续（单个任务失败、网络超时等）
- `CRITICAL`：严重错误导致程序无法运行（数据库连接失败、配置错误等）

**环境差异**：
| 环境 | 日志级别 | 输出目标 | 是否轮转 |
|------|---------|---------|----------|
| 开发环境 | DEBUG | 控制台 + 文件 | 否 |
| 测试环境 | INFO | 控制台 + 文件 | 是 |
| 生产环境 | WARNING | 文件 + 外部日志系统 | 是 |

#### 3.4.2 新功能日志添加要求

**强制要求**：每个新功能或需求必须在以下关键节点添加日志输出：

1. **入口点日志**：
   - API请求接收时记录请求参数（敏感信息脱敏）
   - 定时任务触发时记录任务ID和触发时间
   - 示例：`logger.info(f"Received request: task_id={task_id}, params={params}")`

2. **业务处理日志**：
   - 重要业务逻辑开始前记录输入参数
   - 关键决策点记录判断结果
   - 外部调用（数据库、API、文件操作）前后记录状态
   - 示例：`logger.info(f"Executing SQL query for task {task_id}: {sql_template[:100]}...")`

3. **结果输出日志**：
   - 操作成功时记录关键结果（记录数、文件大小、耗时等）
   - 操作失败时记录详细错误信息和堆栈跟踪
   - 示例：`logger.info(f"Task completed: {record_count} rows exported in {duration}s")`

4. **异常处理日志**：
   - 捕获异常时必须记录错误日志
   - 使用 `exc_info=True` 记录完整堆栈跟踪
   - 示例：`logger.error(f"Operation failed: {str(e)}", exc_info=True)`

5. **性能监控日志**：
   - 耗时操作记录开始和结束时间
   - 大数据量处理记录进度（每N条记录输出一次）
   - 示例：`logger.debug(f"Processing batch {batch_num}/{total_batches}")`

#### 3.4.3 日志内容规范

**必须包含的信息**：
- 操作对象标识（任务ID、用户ID等）
- 操作类型（创建、更新、删除、查询等）
- 关键参数值（脱敏后）
- 操作结果（成功/失败、影响行数等）
- 耗时信息（对于耗时操作）

**敏感信息处理**：
- ❌ 禁止记录明文密码、密钥、Token
- ❌ 禁止记录完整的身份证号、银行卡号
- ✅ 密码等敏感字段应显示为 `***` 或 `[ENCRYPTED]`
- ✅ 手机号、邮箱应部分脱敏：`138****1234`、`us***@example.com`

**日志示例**：
```python
# ✅ 正确的日志
logger.info(f"Creating task: name='{task_name}', datasource_type={datasource_type}")
logger.info(f"SQL execution completed: {record_count} rows fetched in {duration:.2f}s")
logger.error(f"Failed to connect to database: host={host}, port={port}, error={str(e)}", exc_info=True)

# ❌ 错误的日志
logger.info(f"Password: {password}")  # 泄露密码
logger.info("Task created")  # 缺少关键信息
logger.error("Error occurred")  # 缺少上下文
```

#### 3.4.4 日志最佳实践

1. **使用结构化日志**：
   ```python
   # 推荐：使用格式化字符串
   logger.info(f"Task {task_id} executed: status={status}, rows={rows}")
   
   # 不推荐：字符串拼接
   logger.info("Task " + str(task_id) + " executed: status=" + status)
   ```

2. **合理使用日志级别**：
   ```python
   # DEBUG：详细的调试信息
   logger.debug(f"Processing row {row_num}/{total_rows}")
   
   # INFO：关键业务节点
   logger.info(f"Task {task_id} started execution")
   
   # WARNING：需要注意但不影响运行的情况
   logger.warning(f"Query returned no data for task {task_id}")
   
   # ERROR：错误但程序可继续
   logger.error(f"Task {task_id} failed: {error_message}", exc_info=True)
   
   # CRITICAL：严重错误
   logger.critical(f"Database connection lost: {error_message}")
   ```

3. **避免过度日志**：
   - 循环内部避免频繁输出INFO级别日志
   - 大量数据处理的进度日志使用DEBUG级别
   - 生产环境关闭DEBUG日志

4. **日志性能优化**：
   ```python
   # 推荐：先检查日志级别再构造消息
   if logger.isEnabledFor(logging.DEBUG):
       logger.debug(f"Detailed data: {expensive_operation()}")
   
   # 不推荐：无论是否需要都会执行expensive_operation()
   logger.debug(f"Detailed data: {expensive_operation()}")
   ```

### 3.5 文档文件管理规范

#### 3.5.1 Markdown文件存放规则

**核心原则**：所有生成的 `.md` 格式文档必须存放在 `doc/` 目录下，并根据文档类型进行合理组织。

**存放策略**：

1. **优先匹配已有目录**：
   - 如果 `doc/` 下已存在相同类型或主题的目录，新文档应放入该目录
   - 例如：测试相关文档 → `doc/test_coverage_report/` 或现有测试目录
   - 例如：设计规范文档 → `doc/通用文档/`

2. **无匹配目录时放在doc根目录**：
   - 如果找不到合适的子目录，直接将 `.md` 文件放在 `doc/` 根目录下
   - 文件名应清晰表达文档内容，使用英文或拼音命名
   - 例如：`CLAUDE_DESIGN_IMPLEMENTATION.md`、`test_coverage_report_summary.md`

3. **禁止行为**：
   - ❌ 不要在项目根目录创建 `.md` 文件（README.md 除外）
   - ❌ 不要在 `backend/` 或 `frontend/` 目录下创建文档文件
   - ❌ 不要随意创建新的子目录，优先使用现有目录结构

**当前doc目录结构**：
```
doc/
├── need.md                              # 项目开发规范（主文档）
├── CLAUDE_DESIGN_IMPLEMENTATION.md      # Claude设计系统实施指南
├── test_coverage_report_summary.md      # 测试覆盖率报告总结
├── 通用文档/                             # 通用设计文档目录
│   └── ClaudeDESIGN.md                 # Claude设计规范原文档
├── task-scheduler/                       # 需求文档目录
└── test_coverage_report/                 # HTML测试报告目录（不提交Git）
```

**示例场景**：

```bash
# ✅ 正确：新增API文档，doc下无api目录，放在doc根目录
doc/API_DOCUMENTATION.md

# ✅ 正确：新增测试相关文档，放到已有的test_coverage_report目录
doc/test_coverage_report/PERFORMANCE_TEST.md

# ✅ 正确：新增设计规范，放到已有的通用文档目录
doc/通用文档/RESPONSIVE_DESIGN.md

# ❌ 错误：在项目根目录创建文档
/task-scheduler/NEW_FEATURE.md

# ❌ 错误：在backend目录下创建文档
/backend/DEPLOYMENT_GUIDE.md

# ❌ 错误：随意创建新目录
doc/my_new_docs/GUIDE.md  # 应该先确认是否有合适目录可用
```

#### 3.5.2 文档命名规范

- **使用英文或拼音**：避免中文文件名可能导致的跨平台兼容性问题
- **使用大写下划线**：`DOCUMENT_NAME.md` 而非 `document-name.md`
- **语义清晰**：文件名应能准确反映文档内容
- **避免缩写**：除非是广泛认可的缩写（如API、UI、CI等）

**推荐命名**：
- ✅ `DEPLOYMENT_GUIDE.md`
- ✅ `API_REFERENCE.md`
- ✅ `test_coverage_report_summary.md`（已有约定俗成的命名）

**不推荐命名**：
- ❌ `部署指南.md`（中文文件名）
- ❌ `api-ref.md`（过度缩写）
- ❌ `doc1.md`（语义不清）

### 3.6 Git 提交规范

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Type类型**：`feat`（新功能）、`fix`（修复）、`docs`（文档）、`style`（格式）、`refactor`（重构）、`test`（测试）、`chore`（构建/工具）

**示例**：`feat(scheduler): 添加任务优先级调度功能`

**提交频率**：每个功能点/修复单独提交，禁止大杂烩提交。

### 3.7 分支策略

```
main
 └── develop
      ├── feature/task-xxx
      ├── bugfix/issue-xxx
      └── release/v1.0.0
```

- `main`：生产环境代码，仅接受 `release` 分支合并
- `develop`：开发主分支，日常开发基于此
- `feature/*`：新功能开发分支
- `bugfix/*`：缺陷修复分支
- `release/*`：发布准备分支

### 3.8 环境隔离

#### 后端配置（Flask）

```python
# config.py
import os

class BaseConfig:
    # 公共配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '12345678'
    MYSQL_DATABASE = 'task_scheduler_dev'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:3306/{MYSQL_DATABASE}?charset=utf8mb4'

class ProductionConfig(BaseConfig):
    """生产环境配置"""
    DEBUG = False
    DM_HOST = os.getenv('DM_HOST', '192.168.1.100')
    DM_USER = os.getenv('DM_USER', 'SYSDBA')
    DM_PASSWORD = os.getenv('DM_PASSWORD')
    DM_DATABASE = os.getenv('DM_DATABASE', 'TASK_DB')
    SQLALCHEMY_DATABASE_URI = f'dm+dmPython://{DM_USER}:{DM_PASSWORD}@{DM_HOST}:5236/{DM_DATABASE}?charset=utf8'
```

**启动命令**：
```bash
# 开发环境
cd backend
export FLASK_ENV=development
python run.py
# 或 Windows: set FLASK_ENV=development && python run.py

# 生产环境
export FLASK_ENV=production
export DM_HOST=192.168.1.100
export DM_USER=SYSDBA
export DM_PASSWORD=your_password
python run.py
```

#### 前端配置（Vue 3 + Vite）

```javascript
// vite.config.js - 开发环境代理配置
export default defineConfig({
  server: {
    port: 3000,  // 前端开发服务器端口
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',  // 后端API地址
        changeOrigin: true
      }
    }
  }
})
```

**启动命令**：
```bash
# 开发环境
cd frontend
npm install  # 首次需要安装依赖
npm run dev  # 启动开发服务器 (http://localhost:3000)

# 生产环境构建
npm run build  # 生成 dist 目录
# 将 dist 目录部署到 Nginx 或其他 Web 服务器
```

#### 完整开发环境启动流程

**重要提示**：macOS系统默认占用5000端口（AirPlay Receiver），因此后端使用5001端口。

```bash
# 第一步：确保MySQL数据库已创建（仅首次需要）
mysql -u root -p12345678 -e "CREATE DATABASE IF NOT EXISTS task_scheduler_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 终端1 - 启动后端
cd backend
source ../.venv/bin/activate  # 激活虚拟环境
export FLASK_ENV=development
export FLASK_PORT=5001  # macOS使用5001端口，避免与AirPlay冲突
python run.py
# 后端运行在 http://0.0.0.0:5001

# 终端2 - 启动前端
cd frontend
npm run dev
# 前端运行在 http://localhost:3000
# 访问 http://localhost:3000 即可使用系统
```

**常见错误及解决**：
- ❌ `Unknown database 'task_scheduler_dev'` → 执行上面的MySQL创建数据库命令
- ❌ `Port 5000 is in use` → 使用 `export FLASK_PORT=5001` 改用5001端口
- ❌ `Address already in use` → 检查是否有其他进程占用端口，或改用其他端口

#### 生产环境部署

**方案1：前后端分离部署**
```bash
# 1. 后端部署（Windows Server）
# 安装依赖
pip install --no-index --find-links=packages/wheels/ -r requirements.txt
# 设置环境变量
set FLASK_ENV=production
set DM_HOST=192.168.1.100
set DM_USER=SYSDBA
set DM_PASSWORD=your_password
# 启动服务（建议使用 gunicorn 或 IIS）
python run.py

# 2. 前端部署
# 构建前端
cd frontend
npm run build
# 将 dist 目录复制到 Nginx 或 IIS 的 web 根目录
# 配置反向代理：/api -> http://backend-server:5000/api
```

**方案2：Flask 静态文件服务（简单部署）**
```python
# backend/run.py - 生产环境配置
from flask import send_from_directory
import os

@app.route('/')
def index():
    return send_from_directory('../frontend/dist', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('../frontend/dist', path)
```

```bash
# 构建前端
cd frontend
npm run build

# 启动Flask（同时提供前端静态文件和后端API）
cd ../backend
export FLASK_ENV=production
python run.py
# 访问 http://server-ip:5000 即可
```

---

## 📌 4. 项目目录结构

```
task-scheduler/
├── backend/                     # Flask 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/                # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py        # 任务相关接口
│   │   │   └── scheduler.py    # 调度器接口
│   │   ├── models/             # 数据模型（SQLAlchemy）
│   │   │   ├── __init__.py
│   │   │   └── task.py
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   └── task_service.py
│   │   ├── scheduler/          # 定时任务调度
│   │   │   ├── __init__.py
│   │   │   └── job_manager.py
│   │   └── utils/              # 工具函数
│   │       ├── __init__.py
│   │       └── db_helper.py    # 数据库帮助类（支持MySQL/达梦）
│   ├── tests/                  # 测试目录
│   │   ├── unit/               # 单元测试
│   │   ├── integration/        # 接口测试
│   │   └── conftest.py
│   ├── requirements.txt        # 离线依赖清单
│   ├── run.py
│   └── config.py
├── frontend/                   # Vue 前端
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── api/                # API 调用封装
│   │   ├── store/              # Pinia 状态管理
│   │   └── tests/              # 前端测试（Jest/Cypress）
│   ├── package.json
│   └── vite.config.js
├── doc/                        # 文档目录
│   ├── 架构设计.md
│   ├── 达梦数据库连接配置指南.md
│   ├── 部署手册_离线环境.md
│   ├── API文档.md
│   └── 常见问题排查.md
├── packages/                   # 离线依赖包
│   ├── dmPython/
│   ├── sqlalchemy-dm/
│   └── wheels/
├── scripts/                    # 辅助脚本
│   ├── setup_offline_env.bat   # Windows离线环境初始化
│   └── init_db.sql             # 数据库初始化脚本
├── .github/workflows/          # CI 配置
│   └── test-and-report.yml
├── .gitlab-ci.yml              # GitLab CI 配置（备选）
├── .pre-commit-config.yaml     # pre-commit 钩子配置
└── README.md
```

---

## 📌 5. 数据库模型定义示例

```python
# backend/app/models/task.py
from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, comment='任务名称')
    cron_expression = db.Column(db.String(100), nullable=False, comment='Cron表达式')
    command = db.Column(db.Text, nullable=False, comment='执行命令')
    target_server = db.Column(db.String(100), nullable=False, comment='目标服务器')
    status = db.Column(db.SmallInteger, default=0, comment='0-停用 1-启用')
    last_run_time = db.Column(db.DateTime)
    next_run_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cron_expression': self.cron_expression,
            'command': self.command,
            'target_server': self.target_server,
            'status': self.status,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

---

## 📌 6. 定时任务实现规范

```python
# backend/app/scheduler/job_manager.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class JobManager:
    def __init__(self, app=None):
        self.scheduler = BackgroundScheduler()
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.scheduler.start()
        # 应用退出时关闭调度器
        import atexit
        atexit.register(lambda: self.scheduler.shutdown())
    
    def add_job(self, task_id, cron_expression, func):
        """添加定时任务"""
        trigger = CronTrigger.from_crontab(cron_expression)
        job = self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=str(task_id),
            replace_existing=True
        )
        return job
```

---

## 📌 7. 持续集成（CI）规范

### 7.1 触发条件

以下事件自动触发 CI 流程：

| 事件 | 触发动作 |
|------|---------|
| `push` 到 `develop`/`main` | 全量测试 + 覆盖率报告 |
| `pull_request` 到 `main` | 增量测试（仅变更部分）|
| 定时触发（每日凌晨） | 回归测试 + 性能基准测试 |

### 7.2 CI 流程

```yaml
# .github/workflows/test-and-report.yml
name: CI Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      - name: Run unit tests with coverage
        run: |
          cd backend
          pytest tests/unit --cov=app --cov-report=xml --cov-report=html
      - name: Run API tests
        run: |
          cd backend
          pytest tests/integration
      - name: Run frontend tests
        run: |
          cd frontend
          npm ci
          npm run test:unit
          npm run test:e2e
      - name: Generate report
        run: python scripts/generate_report.py
      - name: Send email report
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.qq.com
          server_port: 465
          username: ${{secrets.MAIL_USERNAME}}
          password: ${{secrets.MAIL_PASSWORD}}
          to: 524722511@qq.com
          subject: "task-scheduler 测试报告 - ${{ github.run_id }}"
          body: file://test_report.html
```

### 7.3 代码覆盖率要求

| 模块类型 | 最低覆盖率 |
|---------|-----------|
| 核心业务逻辑 | ≥ 85% |
| API 接口层 | ≥ 80% |
| 工具函数 | ≥ 75% |
| 前端核心组件 | ≥ 70% |

---

## 📌 8. 测试规范

### 8.1 单元测试

```python
# tests/unit/test_task_service.py
import pytest
from app.services.task_service import TaskService

def test_create_task_success(mock_db_session):
    service = TaskService(mock_db_session)
    task = service.create_task(
        name='测试任务',
        cron_expression='0 9 * * *',
        command='echo hello'
    )
    assert task.id is not None
    assert task.name == '测试任务'
```

### 8.2 接口测试

```python
# tests/integration/test_task_api.py
def test_get_tasks(client, auth_headers):
    response = client.get('/api/tasks', headers=auth_headers)
    assert response.status_code == 200
    assert 'data' in response.json
```

### 8.3 前端测试

```javascript
// frontend/tests/unit/TaskForm.spec.js
import { mount } from '@vue/test-utils'
import TaskForm from '@/components/TaskForm.vue'

test('renders form fields', () => {
  const wrapper = mount(TaskForm)
  expect(wrapper.find('input[name="name"]').exists()).toBe(true)
})
```

### 8.4 测试文件组织结构

测试文件必须按照模块进行组织，与源代码目录结构保持一致：

```
tests/
├── unit/                    # 单元测试
│   ├── utils/              # 工具模块测试
│   │   ├── test_time_calculator.py
│   │   └── test_crypto.py
│   ├── models/             # 数据模型测试
│   │   ├── test_sql_export_task.py
│   │   └── test_sql_export_log.py
│   ├── services/           # 业务服务测试
│   │   ├── test_excel_exporter.py
│   │   ├── test_sql_executor.py
│   │   └── test_sql_export_service.py
│   ├── api/                # API路由测试
│   │   └── test_sql_export_api.py
│   └── scheduler/          # 调度器测试
│       └── test_job_manager.py
├── integration/            # 集成测试
│   └── test_full_workflow.py
└── conftest.py             # pytest配置和fixtures
```

**组织原则**：
1. **按模块分类**：每个源代码模块对应一个测试子目录
2. **命名规范**：测试文件以 `test_` 开头，后跟被测试模块名
3. **测试类命名**：以 `Test` 开头，后跟被测试类名
4. **测试方法命名**：以 `test_` 开头，描述测试场景
5. **共享fixtures**：放在 `conftest.py` 中供所有测试使用

### 8.5 测试报告规范

#### 8.5.1 测试报告生成

每次执行测试后必须生成测试报告，包括覆盖率统计和测试结果汇总。

**生成命令**：
```bash
# 生成终端报告（包含缺失行信息）
cd backend
python -m pytest tests/unit/ --cov=app --cov-report=term-missing

# 生成HTML可视化报告
python -m pytest tests/unit/ --cov=app --cov-report=html:../doc/test_coverage_report

# 生成XML报告（用于CI/CD集成）
python -m pytest tests/unit/ --cov=app --cov-report=xml:../doc/test_coverage_report/coverage.xml
```

**报告存放位置**：
- HTML报告：`doc/test_coverage_report/` 目录
- XML报告：`doc/test_coverage_report/coverage.xml`
- 报告不提交到Git仓库，需在 `.gitignore` 中排除

#### 8.5.2 测试报告内容要求

测试报告必须包含以下信息：

1. **覆盖率统计**：
   - 整体覆盖率（Statements、Miss、Cover%）
   - 各模块详细覆盖率
   - 未覆盖的代码行号（Missing列）

2. **测试结果汇总**：
   - 总测试用例数
   - 通过数量（PASSED）
   - 失败数量（FAILED）
   - 错误数量（ERROR）
   - 警告信息（Warnings）

3. **失败用例清单**：
   - 失败的测试用例名称
   - 失败原因和堆栈跟踪
   - 预期结果与实际结果对比

4. **性能指标**（可选）：
   - 测试执行总耗时
   - 单个测试用例执行时间
   - 慢测试预警（>1秒）

#### 8.5.3 CI流程中的测试报告

在CI/CD流程中，测试报告自动生成并通过邮件发送：

```yaml
# .github/workflows/test-and-report.yml
name: CI Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests with coverage
        run: |
          cd backend
          pytest tests/unit --cov=app --cov-report=xml --cov-report=html
      
      - name: Generate HTML report
        run: |
          cd backend
          python -m pytest tests/unit/ --cov=app --cov-report=html:../doc/test_coverage_report
      
      - name: Archive test reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: doc/test_coverage_report/
      
      - name: Send email report
        if: always()  # 无论测试是否通过都发送邮件
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.qq.com
          server_port: 465
          username: ${{secrets.MAIL_USERNAME}}
          password: ${{secrets.MAIL_PASSWORD}}
          to: 524722511@qq.com
          subject: "task-scheduler 测试报告 - ${{ github.run_id }}"
          body: |
            测试执行完成，详情请查看附件HTML报告。
            
            关键指标：
            - 测试总数: ${{ steps.test-summary.outputs.total }}
            - 通过: ${{ steps.test-summary.outputs.passed }}
            - 失败: ${{ steps.test-summary.outputs.failed }}
            - 覆盖率: ${{ steps.coverage-summary.outputs.percentage }}%
          attachments: doc/test_coverage_report/index.html
```

#### 8.5.4 测试报告查看方式

**本地查看HTML报告**：
```bash
# macOS
open doc/test_coverage_report/index.html

# Linux
xdg-open doc/test_coverage_report/index.html

# Windows
start doc/test_coverage_report/index.html
```

**报告内容包括**：
- 覆盖率概览图表
- 各模块覆盖率排名
- 可点击的源代码视图（高亮显示未覆盖行）
- 历史趋势对比（需配合CI持续收集）

#### 8.5.5 测试报告归档要求

1. **开发阶段**：每次功能开发完成后，生成本地测试报告并验证覆盖率达标
2. **提测阶段**：提交Pull Request时，CI自动运行测试并生成报告
3. **发布阶段**：每个Release版本必须附带完整的测试报告
4. **回归测试**：每日定时任务触发全量回归测试，生成日报并通过邮件发送

#### 8.5.6 测试报告邮件模板

邮件主题格式：`task-scheduler 测试报告 - [构建ID] - [日期]`

邮件正文包含：
- 构建基本信息（分支、Commit ID、触发者）
- 测试结果摘要（通过/失败/错误数量）
- 覆盖率变化趋势（较上次构建提升/下降百分比）
- 失败用例清单（仅当有失败时）
- HTML报告下载链接或附件
- 建议操作（通过则合并，失败则修复）

#### 8.5.7 代码变更时的测试更新要求

**核心原则**：代码与测试必须同步更新，确保测试始终反映最新业务逻辑。

**具体要求**：

1. **新增功能时**：
   - 必须同时编写对应的单元测试
   - 测试用例覆盖正常流程、边界情况、异常处理
   - 确保新代码的覆盖率达到85%以上

2. **修改现有代码时**：
   - **必须检查并更新相关测试用例**，确保测试覆盖所有变动点
   - 如果修改了函数签名、返回值或业务逻辑，必须同步更新测试断言
   - 如果新增了分支逻辑，必须补充对应的测试场景
   - 如果删除了代码，必须清理不再需要的测试用例

3. **重构代码时**：
   - 先运行现有测试，确保全部通过（建立基准）
   - 执行重构
   - 再次运行测试，确保行为未改变
   - 如有必要，补充新的测试用例以增强覆盖

4. **修复Bug时**：
   - **必须先编写复现Bug的失败测试**（TDD红-绿-重构流程）
   - 修复Bug使测试通过
   - 确保该测试永久保留，防止回归

**示例场景**：

```python
# 场景1：修改函数返回值
# 原代码
def calculate_total(items):
    return sum(item.price for item in items)

# 测试
def test_calculate_total():
    items = [Item(price=10), Item(price=20)]
    assert calculate_total(items) == 30

# 修改后：增加了折扣逻辑
def calculate_total(items, discount=0):
    total = sum(item.price for item in items)
    return total * (1 - discount)

# 必须更新测试
def test_calculate_total_with_discount():
    items = [Item(price=10), Item(price=20)]
    # 测试无折扣
    assert calculate_total(items) == 30
    # 测试有折扣
    assert calculate_total(items, discount=0.1) == 27

# 场景2：新增分支逻辑
# 原代码
def get_status(task):
    return task.status

# 修改后：增加了过期判断
def get_status(task):
    if task.is_expired:
        return 'expired'
    return task.status

# 必须补充测试
def test_get_status_expired():
    task = Task(status='active', is_expired=True)
    assert get_status(task) == 'expired'

def test_get_status_active():
    task = Task(status='active', is_expired=False)
    assert get_status(task) == 'active'
```

**检查清单**：
- [ ] 是否更新了所有受影响的测试用例？
- [ ] 是否覆盖了新增的代码分支？
- [ ] 是否验证了修改后的业务逻辑？
- [ ] 运行完整测试套件，是否全部通过？
- [ ] 覆盖率是否仍保持在85%以上？
- [ ] 主流程是否正常执行？

---

## 📌 9. 注意事项

1. **数据库环境切换**：开发环境使用MySQL（账号root/密码12345678），生产环境使用达梦数据库。通过环境变量或配置文件区分不同环境的数据库连接。
2. **离线依赖包准备**：本项目部署在Windows Server离线环境中，无法访问外部网络。必须在开发阶段提前下载所有Windows平台的依赖包（.whl文件），统一放入 `packages/wheels/` 目录。
   - 下载命令：`pip download -d packages/wheels/ -r backend/requirements.txt --platform win_amd64 --only-binary=:all:`
   - 安装命令（离线环境）：`pip install --no-index --find-links=packages/wheels/ -r backend/requirements.txt`
3. **达梦数据库驱动必须离线安装**：项目部署在Windows Server离线环境中，所有依赖包（dmPython、sqlalchemy-dm等）必须在开发阶段提前准备，统一放入 `packages/` 目录。
4. **环境变量配置**：达梦数据库的 `bin` 目录必须添加到系统 `PATH` 环境变量，否则dmPython加载会失败。
5. **Python版本要求**：必须使用 **Python 3.13.3**（或3.13.x系列），其他主版本可能存在兼容性问题。
6. **SQLAlchemy版本锁定**：建议使用 **2.0.36**，更高版本可能与达梦方言包不兼容。
7. **连接池维护**：必须配置 `pool_pre_ping=True` 处理长连接断开问题。
8. **事务管理**：所有写操作必须显式提交或回滚，禁止依赖自动提交。
9. **日志记录**：数据库操作必须记录详细日志，便于问题排查。
10. **CI邮箱配置**：QQ邮箱的 `smtp.qq.com` 需要开启SMTP服务并使用授权码，请妥善保管。
11. **测试覆盖率要求**：
    - **新增代码必须编写对应的单元测试**，测试文件按模块组织在 `tests/unit/` 目录下
    - **变更代码需要同步调整测试代码**，确保测试用例覆盖所有变动点
    - **核心业务逻辑覆盖率不低于85%**，重点保证主流程的正常执行
    - **每次提交前必须运行测试**，确保所有测试通过且覆盖率达标
    - **CI流程自动检查覆盖率**，低于85%的PR将被拒绝合并

---

## 📌 10. 常见问题（FAQ）

| 问题 | 解决方案 |
|------|---------|
| `No module named 'pymysql'` | 执行 `pip install pymysql` 安装MySQL驱动 |
| MySQL连接失败 | 检查MySQL服务是否启动，确认账号密码正确（root/12345678） |
| `No module named 'dmPython'` | 确保达梦安装目录的 `bin` 已添加到系统 `PATH`，并离线编译安装dmPython |
| `Can't load plugin: sqlalchemy.dialects:dm.dmPython` | 确保已安装 `sqlalchemy-dm` 方言包 |
| 连接长时间闲置后断开 | 设置 `pool_pre_ping=True`，连接前自动检测 |
| 批量插入速度慢 | 使用 `executemany` 分批插入，每批2000-5000条 |
| 字符集乱码 | 连接字符串添加 `?charset=utf8mb4`（MySQL）或 `?charset=utf8`（达梦） |
| CI 推送 QQ 邮箱失败 | 检查 SMTP 服务器配置，使用 QQ 邮箱授权码而非登录密码 |

---

## 📌 11. 参考文档

| 文档名称 | 位置/链接 |
|---------|----------|
| Claude设计系统实施指南 | `doc/CLAUDE_DESIGN_IMPLEMENTATION.md` |
| Claude设计风格快速参考 | `frontend/CLAUDE_QUICK_REFERENCE.md` |
| Claude设计规范原文档 | `doc/通用文档/ClaudeDESIGN.md` |
| 测试覆盖率报告总结 | `doc/test_coverage_report_summary.md` |
| SQLAlchemy官方文档 | https://docs.sqlalchemy.org/ |
| Flask-SQLAlchemy文档 | https://flask-sqlalchemy.palletsprojects.com/ |
| APScheduler文档 | https://apscheduler.readthedocs.io/ |
| pytest文档 | https://docs.pytest.org/ |
| Vue 3官方文档 | https://vuejs.org/ |
| Element Plus文档 | https://element-plus.org/ |

---

## 📌 12. 版本记录

| 版本 | 日期 | 变更说明 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-04-20 | 初始版本，规范双数据库策略（开发用MySQL/生产用达梦）与CI流程 | AI Agent |
| v1.1 | 2026-04-20 | 新增测试文件组织规范，明确按模块分类的测试结构；更新SQLAlchemy版本为2.0.36；添加测试覆盖率要求 | AI Agent |
| v1.2 | 2026-04-20 | 新增Vue 3前端项目结构与代码；完善环境隔离配置，补充前后端启动命令和部署方案 | AI Agent |
| v1.3 | 2026-04-20 | 大幅提升测试覆盖率（26%→67%），新增服务层、API层、调度器单元测试；补充测试报告规范，包括生成命令、内容要求、CI集成、邮件模板等 | AI Agent |
| v1.4 | 2026-04-20 | 强化测试覆盖率要求：明确变更代码需同步更新测试、主流程覆盖率≥85%、提交前必须运行测试、CI自动检查；新增8.5.7节详细说明代码变更时的测试更新要求和示例 | AI Agent |
| v1.5 | 2026-04-20 | 新增日志规范要求（3.4节）：定义日志配置、分级输出、新功能日志添加强制要求、敏感信息处理规范；为所有后端代码添加完善的日志系统 | AI Agent |

---

**本规范自发布之日起生效，所有开发者（包括AI智能体）在参与task-scheduler项目开发时，必须严格遵循以上规范。违反规范的代码将被拒绝合并。**