# Windows Server 2012 R2 部署快速参考

> 一键查看部署流程和关键命令

---

## 📦 开发机准备（有网络）

### 步骤 1：打包后端依赖

```powershell
# 在 macOS/Linux 开发机上
cd backend
pip download -r requirements.txt -d offline_packages
```

或 Windows 开发机：
```powershell
cd scripts
.\prepare_offline_packages.bat
```

### 步骤 2：构建前端

```powershell
cd frontend
npm install
npm run build
# 生成 dist 文件夹
```

### 步骤 3：打包部署包

```
task-scheduler-deploy/
├── backend/
│   ├── app/              # 源码
│   ├── config.py
│   ├── run.py
│   ├── requirements.txt
│   ├── .env.production   # 修改好配置
│   └── offline_packages/ # Python 依赖
├── frontend/dist/        # 构建产物
├── scripts/
│   ├── install_backend.bat
│   └── start_service.bat
└── OFFLINE_DEPLOYMENT_WINDOWS.md
```

---

## 🖥️ 目标服务器部署（无网络）

### 环境要求

| 软件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 必须安装 |
| MySQL | 8.0+ | 开发环境 |
| 达梦 DM8 | - | 生产环境 |
| Node.js | 18+ | 仅开发时需要 |

### 快速部署（3 步）

#### 1. 安装后端

```powershell
cd D:\task-scheduler\backend
.\install_backend.bat
# 或
python -m venv venv
venv\Scripts\pip install --no-index --find-links=offline_packages -r requirements.txt
```

#### 2. 配置环境

编辑 `backend\.env.production`：

```ini
FLASK_ENV=production
FLASK_PORT=5000
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-32-char-encryption-key

# 达梦数据库
DM_USER=SYSDBA
DM_PASSWORD=your_password
DM_HOST=127.0.0.1
DM_PORT=5236
DM_DATABASE=TASK_DB
```

#### 3. 启动服务

```powershell
cd D:\task-scheduler\backend
.\start_service.bat
```

访问：http://localhost:5000

---

## 🔧 可选：配置 Nginx

### nginx.conf

```nginx
server {
    listen 80;
    
    location / {
        root D:/task-scheduler/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:5000;
    }
}
```

### 启动 Nginx

```powershell
cd D:\nginx
start nginx.exe
```

---

## 🗄️ 数据库初始化

### MySQL

```sql
CREATE DATABASE task_scheduler_dev 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 执行 init_db.sql
mysql -u root -p task_scheduler_dev < init_db.sql
```

### 达梦

```sql
-- 创建数据库（使用 DM 管理工具）
-- 然后执行 init_db.sql
```

---

## 📝 生产环境 .env.production 模板

```ini
# Flask 配置
FLASK_ENV=production
FLASK_PORT=5000
SECRET_KEY=your-very-strong-secret-key-please-change

# 加密
ENCRYPTION_KEY=your-32-characters-encryption-key

# 达梦数据库（生产）
DM_USER=SYSDBA
DM_PASSWORD=your_dm_password
DM_HOST=192.168.1.100
DM_PORT=5236
DM_DATABASE=TASK_DB

# 导出路径
EXPORT_DEFAULT_PATH=D:/task-scheduler/exports/
```

---

## ⚡ 常用命令

### 服务管理

```powershell
# 启动服务
cd backend
.\start_service.bat

# 停止服务（Ctrl+C）

# 查看日志
type app.log
```

### 数据库备份

```powershell
# MySQL
mysqldump -u root -p task_scheduler_dev > backup.sql

# 达梦
dexp SYSDBA/password@localhost/TASK_DB file=backup.dmp
```

### 更新应用

```powershell
# 1. 停止服务
# Ctrl+C

# 2. 备份
xcopy D:\task-scheduler D:\backup /s /e /y

# 3. 更新依赖
cd D:\task-scheduler\backend
venv\Scripts\pip install --upgrade --no-index --find-links=offline_packages -r requirements.txt

# 4. 启动服务
.\start_service.bat
```

---

## ⚠️ 常见问题

### Q1: Python 版本不对

```powershell
python --version
# 必须 3.10+
# 下载：https://www.python.org/downloads/windows/
```

### Q2: 端口被占用

修改 `.env.production`：
```ini
FLASK_PORT=5001
```

### Q3: 达梦驱动缺失

```powershell
# 从达梦安装包获取
cd D:\DM8\drivers\python

# 安装 dmPython
cd dmPython
python setup.py install

# 安装 sqlalchemy_dm
cd ..\sqlalchemy_dm
python setup.py install
```

### Q4: 无法访问前端

```powershell
# 检查后端
curl http://localhost:5000/api/sql-export/tasks

# 检查 Nginx
curl http://localhost

# 检查防火墙
netsh advfirewall firewall show rule name=all
```

---

## 📞 技术支持

- 详细文档：`OFFLINE_DEPLOYMENT_WINDOWS.md`
- 日志文件：`backend/app.log`
- 错误排查：检查 `backend/app.log` 中的 ERROR 级别日志
