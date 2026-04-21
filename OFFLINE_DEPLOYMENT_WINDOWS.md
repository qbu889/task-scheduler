# Windows Server 2012 R2 离线部署指南

> 适用于无网络环境的完整部署方案

---

## 一、在开发机上准备离线包

### 1.1 准备后端 Python 依赖包

在**有网络的开发机**（建议与目标服务器同系统）上执行：

```powershell
# 进入后端目录
cd backend

# 下载所有依赖到 wheels 文件夹
pip download -r requirements.txt -d ./offline_packages

# 如果需要支持达梦数据库，额外下载（需先获取达梦驱动源码）
# 从达梦数据库安装目录获取：
# - D:\DM8\drivers\python\dmPython-*.tar.gz
# - D:\DM8\drivers\python\sqlalchemy_dm-*.tar.gz
```

### 1.2 构建前端静态文件

```powershell
# 进入前端目录
cd frontend

# 安装依赖（需要网络）
npm install

# 构建生产版本
npm run build

# dist 文件夹将包含所有静态文件
```

### 1.3 准备部署包结构

创建部署文件夹 `task-scheduler-deploy`：

```
task-scheduler-deploy/
├── backend/
│   ├── app/                    # 后端源码
│   ├── tests/                  # 测试代码（可选）
│   ├── config.py               # 配置文件
│   ├── run.py                  # 启动文件
│   ├── requirements.txt        # 依赖清单
│   ├── .env.production        # 生产环境配置
│   └── offline_packages/       # Python 依赖离线包
├── frontend/dist/              # 前端构建后的静态文件
├── scripts/
│   ├── init_db.sql            # 数据库初始化脚本
│   ├── install_backend.bat    # 后端安装脚本
│   ├── install_frontend.bat   # 前端安装脚本
│   └── start_service.bat      # 服务启动脚本
└── README.md                  # 本文件
```

---

## 二、目标服务器环境要求

### 2.1 必须安装的软件

- **Python 3.10+**（Windows 安装包）
  - 下载：https://www.python.org/downloads/windows/
  - 安装时勾选 "Add Python to PATH"
  
- **Node.js 18+**（可选，仅用于前端开发/重新构建）
  - 如需提前构建，在生产机不需要
  
- **MySQL 8.0+**（开发环境）或 **达梦数据库 DM8**（生产环境）

### 2.2 检查 Python 版本

```powershell
python --version
# 应显示 Python 3.10.x 或更高
```

---

## 三、部署步骤

### 3.1 复制部署包到目标服务器

将整个 `task-scheduler-deploy` 文件夹复制到目标服务器，例如：

```
D:\task-scheduler\
```

### 3.2 安装后端依赖（离线）

创建 `install_backend.bat`：

```batch
@echo off
echo ==========================================
echo Task Scheduler 后端依赖安装（离线模式）
echo ==========================================

cd /d D:\task-scheduler\backend

echo.
echo [1/3] 检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo [2/3] 创建虚拟环境...
python -m venv venv

echo.
echo [3/3] 离线安装依赖包...
venv\Scripts\pip install --no-index --find-links=offline_packages -r requirements.txt

echo.
echo ==========================================
echo 后端依赖安装完成！
echo ==========================================
pause
```

执行安装：

```powershell
cd D:\task-scheduler\backend
.\install_backend.bat
```

### 3.3 配置数据库

#### 选项 A：MySQL（开发环境）

1. 安装 MySQL 8.0
2. 创建数据库：

```sql
CREATE DATABASE task_scheduler_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. 执行初始化脚本：

```powershell
mysql -u root -p task_scheduler_dev < D:\task-scheduler\scripts\init_db.sql
```

#### 选项 B：达梦数据库（生产环境）

1. 安装达梦数据库 DM8
2. 创建数据库（使用 DM 管理工具或 SQL）：

```sql
CREATE DATABASE "TASK_DB" CHARACTER SET UTF8;
```

3. 执行初始化脚本（使用 DM 的 isql 工具）：

```powershell
isql -U SYSDBA -P your_password -d TASK_DB -f D:\task-scheduler\scripts\init_db.sql
```

4. **安装达梦驱动**（需从达梦安装包获取）：

```powershell
# 复制达梦驱动到后端目录
xcopy D:\DM8\drivers\python\dmPython D:\task-scheduler\backend\offline_packages\ /s /y
xcopy D:\DM8\drivers\python\sqlalchemy_dm D:\task-scheduler\backend\offline_packages\ /s /y

# 安装驱动
cd D:\task-scheduler\backend
venv\Scripts\pip install --no-index --find-links=offline_packages dmPython sqlalchemy_dm
```

### 3.4 配置环境变量

编辑 `backend\.env.production`：

```ini
# 应用配置
FLASK_ENV=production
FLASK_PORT=5000
SECRET_KEY=your-very-strong-secret-key-change-this

# 加密密钥（用于数据源密码加密）
ENCRYPTION_KEY=your-encryption-key-32-characters

# 达梦数据库配置
DM_USER=SYSDBA
DM_PASSWORD=your_dm_password
DM_HOST=127.0.0.1
DM_PORT=5236
DM_DATABASE=TASK_DB

# 导出路径
EXPORT_DEFAULT_PATH=D:/task-scheduler/exports/
```

### 3.5 初始化后端服务

```powershell
cd D:\task-scheduler\backend

# 初始化数据库表
venv\Scripts\python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all()"

# 创建导出目录
mkdir D:\task-scheduler\exports
```

### 3.6 配置前端静态文件

创建 `install_frontend.bat`（如果使用 Nginx）：

```batch
@echo off
echo ==========================================
echo 前端静态文件配置
echo ==========================================

echo.
echo 前端文件已构建在 dist 目录中
echo 请按照 README 配置 Nginx 反向代理
echo.

echo 源文件位置：D:\task-scheduler\frontend\dist
echo.

pause
```

### 3.7 启动服务

#### 方式 A：直接启动（测试用）

```powershell
cd D:\task-scheduler\backend
venv\Scripts\python run.py
```

访问：http://localhost:5000

#### 方式 B：Windows 服务（生产环境）

创建 `start_service.bat`：

```batch
@echo off
echo ==========================================
echo 启动 Task Scheduler 服务
echo ==========================================

cd /d D:\task-scheduler\backend

echo.
echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo [2/2] 启动 Flask 应用...
python run.py

pause
```

#### 方式 C：使用 NSSM 注册为 Windows 服务

1. 下载 NSSM：https://nssm.cc/download
2. 安装服务：

```powershell
nssm install TaskScheduler "D:\task-scheduler\backend\venv\Scripts\python.exe" "D:\task-scheduler\backend\run.py"
nssm set TaskScheduler AppDirectory "D:\task-scheduler\backend"
nssm set TaskScheduler DisplayName "Task Scheduler Service"
nssm start TaskScheduler
```

### 3.8 配置 Nginx（推荐）

1. 下载 Nginx for Windows：http://nginx.org/en/download.html
2. 解压到 `D:\nginx`
3. 配置 `D:\nginx\conf\nginx.conf`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root D:/task-scheduler/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件下载
    location /downloads {
        alias D:/task-scheduler/exports;
        autoindex on;
    }
}
```

4. 启动 Nginx：

```powershell
cd D:\nginx
start nginx.exe
```

---

## 四、验证部署

### 4.1 检查后端服务

```powershell
# 测试 API
curl http://localhost:5000/api/sql-export/tasks

# 应返回 JSON 格式的任务列表
```

### 4.2 访问前端

打开浏览器访问：

- 直接访问后端：http://localhost:5000
- 通过 Nginx：http://localhost

### 4.3 测试功能

1. 登录管理界面
2. 创建测试任务
3. 手动触发执行
4. 检查导出文件

---

## 五、常见问题

### Q1: pip 安装提示依赖缺失

**解决**：确保 `offline_packages` 文件夹包含所有依赖及其子依赖：

```powershell
# 在开发机上重新下载所有依赖
pip download -r requirements.txt -d ./offline_packages --platform win_amd64 --only-binary=:all:
```

### Q2: 达梦驱动编译失败

**解决**：Windows 上需要提前安装 Visual C++ 编译工具：
- 下载：Visual Studio Build Tools
- 安装 "Desktop development with C++" 组件

或使用预编译的 `.whl` 文件。

### Q3: 服务启动后端口被占用

**解决**：修改 `.env.production` 中的端口：

```ini
FLASK_PORT=5001
```

### Q4: 导出文件无法下载

**解决**：检查导出目录权限：

```powershell
# 确保 IIS_IUSRS 或当前用户有写入权限
icacls D:\task-scheduler\exports /grant Everyone:F
```

---

## 六、维护

### 6.1 查看服务日志

```powershell
# 如果使用 NSSM
nssm status TaskScheduler
```

### 6.2 更新应用

```powershell
# 1. 停止服务
nssm stop TaskScheduler

# 2. 备份当前版本
xcopy D:\task-scheduler D:\task-scheduler-backup /s /e /y

# 3. 复制新版本
xcopy D:\new-version\backend D:\task-scheduler\backend /s /e /y

# 4. 更新依赖（如有新依赖）
cd D:\task-scheduler\backend
venv\Scripts\pip install --no-index --find-links=offline_packages -r requirements.txt

# 5. 启动服务
nssm start TaskScheduler
```

### 6.3 数据库备份

```powershell
# MySQL 备份
mysqldump -u root -p task_scheduler_dev > D:\backup\task_scheduler_$(date +%Y%m%d).sql

# 达梦备份（使用 DM 管理工具或 dexp 命令）
dexp SYSDBA/your_password@localhost:5236/TASK_DB file=D:\backup\task_scheduler_$(date +%Y%m%d).dmp
```

---

## 七、性能优化

### 7.1 配置 Python 环境变量

```powershell
# 优化 Python 性能
setx PYTHONOPTIMIZE 1
setx PYTHONDONTWRITEBYTECODE 1
```

### 7.2 配置日志轮转

编辑 `backend\run.py`，添加日志轮转：

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
```

---

## 八、安全建议

1. **修改默认密钥**：
   - `SECRET_KEY`
   - `ENCRYPTION_KEY`

2. **防火墙配置**：
   ```powershell
   # 仅开放必要端口
   netsh advfirewall firewall add rule name="Task Scheduler" dir=in action=allow protocol=TCP localport=80
   ```

3. **定期更新**：
   - Python 依赖包（在有网络环境更新后重新打包）
   - 操作系统补丁
   - 数据库安全更新

---

**部署完成后，请参考用户手册进行系统配置和使用。**
