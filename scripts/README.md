# Task Scheduler 启动脚本使用说明

本文档说明如何使用项目中的启动脚本来快速启动开发环境和生产环境。

## 📁 脚本位置

所有启动脚本位于 `scripts/` 目录下：

```
scripts/
├── start_dev.sh          # 开发环境启动脚本 (macOS/Linux)
├── start_dev.bat         # 开发环境启动脚本 (Windows)
├── start_prod.sh         # 生产环境启动脚本 (macOS/Linux)
└── start_prod.bat        # 生产环境启动脚本 (Windows)
```

## 🚀 开发环境启动

### macOS / Linux

```bash
# 方式1：直接运行脚本（推荐）
cd scripts
./start_dev.sh

# 方式2：从项目根目录运行
bash scripts/start_dev.sh
```

**脚本功能**：
1. ✅ 自动检查Python和Node.js环境
2. ✅ 自动创建并激活Python虚拟环境
3. ✅ 自动初始化MySQL数据库（如需要）
4. ✅ 自动安装后端依赖（requirements.txt）
5. ✅ 自动安装前端依赖（node_modules）
6. ✅ 同时启动后端（5001端口）和前端（3000端口）
7. ✅ 按 Ctrl+C 可同时停止两个服务

**访问地址**：
- 前端界面：http://localhost:3000
- 后端API：http://localhost:5001

### Windows

```batch
REM 双击运行或在命令行执行
scripts\start_dev.bat
```

**特点**：
- 后端和前端分别在独立窗口中启动
- 便于分别查看日志和调试
- 关闭窗口即可停止对应服务

---

## 🏭 生产环境启动

### 前置要求

生产环境启动前，必须设置以下环境变量：

```bash
# 达梦数据库配置
export DM_HOST=192.168.1.100
export DM_USER=SYSDBA
export DM_PASSWORD=your_password
export DM_DATABASE=TASK_DB
```

### macOS / Linux

```bash
# 设置环境变量
export DM_HOST=192.168.1.100
export DM_USER=SYSDBA
export DM_PASSWORD=your_password
export DM_DATABASE=TASK_DB

# 启动生产环境
cd scripts
./start_prod.sh
```

**脚本功能**：
1. ✅ 验证必需的环境变量是否已设置
2. ✅ 激活Python虚拟环境
3. ✅ 检查并安装后端依赖
4. ✅ 以生产模式启动后端服务（5000端口）
5. ✅ 关闭调试模式，启用日志记录

**注意**：生产环境只启动后端服务，前端需要单独构建并部署到Nginx或其他Web服务器。

### Windows

```batch
REM 设置环境变量
set DM_HOST=192.168.1.100
set DM_USER=SYSDBA
set DM_PASSWORD=your_password
set DM_DATABASE=TASK_DB

REM 启动生产环境
scripts\start_prod.bat
```

---

## 📝 环境配置文件

项目提供了环境配置文件模板，可根据实际情况修改：

### 后端配置

- `backend/.env.development` - 开发环境配置
  - MySQL数据库连接
  - Flask调试模式开启
  - 端口：5001

- `backend/.env.production` - 生产环境配置
  - 达梦数据库连接
  - Flask调试模式关闭
  - 端口：5000

**使用方式**：
```bash
# 开发环境加载配置
source backend/.env.development

# 生产环境加载配置
source backend/.env.production
```

### 前端配置

- `frontend/.env.development` - 开发环境配置
  - API代理指向 http://localhost:5001/api

- `frontend/.env.production` - 生产环境配置
  - API使用相对路径 /api（通过Nginx反向代理）

---

## 🔧 手动启动（不使用脚本）

如果需要使用自定义配置或调试，可以手动启动服务。

### 后端手动启动

```bash
# 1. 激活虚拟环境
cd /path/to/task-scheduler
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 2. 设置环境变量
export FLASK_ENV=development
export FLASK_PORT=5001
export MYSQL_HOST=127.0.0.1
export MYSQL_USER=root
export MYSQL_PASSWORD=12345678

# 3. 启动服务
cd backend
python run.py
```

### 前端手动启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖（首次需要）
npm install

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

---

## ⚠️ 常见问题

### 1. 权限问题（macOS/Linux）

如果遇到 "Permission denied" 错误：

```bash
chmod +x scripts/start_dev.sh scripts/start_prod.sh
```

### 2. 端口被占用

**macOS**：5000端口被AirPlay Receiver占用，开发环境默认使用5001端口。

解决方法：
```bash
# 使用其他端口
export FLASK_PORT=5002
python run.py
```

### 3. 数据库连接失败

检查MySQL是否运行：
```bash
# macOS
brew services list | grep mysql

# Linux
systemctl status mysql

# 启动MySQL
brew services start mysql  # macOS
sudo systemctl start mysql # Linux
```

### 4. Python虚拟环境问题

重新创建虚拟环境：
```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 5. Node.js版本过低

确保Node.js版本 >= 16：
```bash
node --version
```

如需升级，推荐使用nvm：
```bash
nvm install 18
nvm use 18
```

---

## 📊 环境对比

| 特性 | 开发环境 (dev) | 生产环境 (prod) |
|------|---------------|----------------|
| 数据库 | MySQL | 达梦数据库 DM8 |
| Flask调试 | 开启 | 关闭 |
| 日志级别 | INFO | WARNING |
| 后端端口 | 5001 | 5000 |
| 前端端口 | 3000 | 需构建后部署 |
| 热重载 | 支持 | 不支持 |
| 错误追踪 | 详细堆栈 | 简化错误信息 |
| 环境变量 | .env.development | 系统环境变量 |

---

## 🔐 安全提示

1. **不要将 `.env.production` 提交到版本控制系统**
   - 已在 `.gitignore` 中排除
   - 生产环境应使用系统环境变量或密钥管理服务

2. **修改默认密码**
   - 开发环境MySQL密码：12345678
   - 生产环境务必使用强密码

3. **SECRET_KEY安全**
   - 生产环境必须使用随机生成的强密钥
   - 可使用以下命令生成：
     ```python
     python -c "import secrets; print(secrets.token_hex(32))"
     ```

4. **数据库访问控制**
   - 生产环境限制数据库IP白名单
   - 使用最小权限原则分配数据库用户权限

---

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件：`backend/app.log`
2. 前端控制台：浏览器开发者工具
3. 后端控制台：启动脚本的输出信息

更多详细信息请参考：
- [项目开发规范](../doc/need.md)
- [Claude设计系统实施指南](../doc/CLAUDE_DESIGN_IMPLEMENTATION.md)
