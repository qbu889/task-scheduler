# 🚀 Task Scheduler 快速启动指南

## ⚡ 最快速的启动方式

### macOS / Linux 用户

```bash
# 一行命令启动开发环境
cd scripts && ./start_dev.sh
```

等待脚本自动完成以下操作：
- ✅ 创建Python虚拟环境
- ✅ 安装所有依赖
- ✅ 初始化MySQL数据库
- ✅ 启动后端服务 (http://localhost:5001)
- ✅ 启动前端服务 (http://localhost:3000)

**访问**: http://localhost:3000

---

### Windows 用户

```batch
REM 双击运行或在命令行执行
scripts\start_dev.bat
```

会自动打开两个窗口：
- 后端服务窗口
- 前端服务窗口

**访问**: http://localhost:3000

---

## 📋 首次使用检查清单

在启动前，请确保已安装：

- [ ] Python 3.10+ ([下载](https://www.python.org/downloads/))
- [ ] Node.js 16+ ([下载](https://nodejs.org/))
- [ ] MySQL 5.7+ ([下载](https://dev.mysql.com/downloads/))

检查安装：
```bash
python --version    # 应显示 Python 3.10.x 或更高
node --version      # 应显示 v16.x.x 或更高
mysql --version     # 应显示 mysql 5.7.x 或更高
```

---

## 🔧 常见问题速查

### 1️⃣ 端口被占用

**错误**: `Address already in use` 或 `Port 5001 is in use`

**解决**:
```bash
# macOS - 查找并关闭占用端口的进程
lsof -i :5001
kill -9 <PID>

# 或使用其他端口
export FLASK_PORT=5002
python run.py
```

### 2️⃣ 数据库连接失败

**错误**: `Unknown database 'task_scheduler_dev'`

**解决**:
```bash
# 创建数据库
mysql -u root -p12345678 -e "CREATE DATABASE IF NOT EXISTS task_scheduler_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

**错误**: `Access denied for user 'root'@'localhost'`

**解决**:
- 检查MySQL是否运行
- 确认密码正确（默认：12345678）
- 修改 `backend/.env.development` 中的密码

### 3️⃣ Python虚拟环境问题

**错误**: `ModuleNotFoundError: No module named 'flask'`

**解决**:
```bash
# 重新创建虚拟环境
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 4️⃣ Node.js依赖问题

**错误**: `Cannot find module 'vue'`

**解决**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 5️⃣ 权限问题 (macOS/Linux)

**错误**: `Permission denied`

**解决**:
```bash
chmod +x scripts/start_dev.sh scripts/start_prod.sh
```

---

## 🎯 常用命令速查

### 开发环境

```bash
# 启动所有服务（推荐）
./scripts/start_dev.sh

# 只启动后端
cd backend && source ../.venv/bin/activate && python run.py

# 只启动前端
cd frontend && npm run dev

# 查看后端日志
tail -f backend/app.log

# 运行测试
cd backend && pytest tests/unit -v
```

### 生产环境

```bash
# 设置环境变量
export DM_HOST=192.168.1.100
export DM_USER=SYSDBA
export DM_PASSWORD=your_password
export DM_DATABASE=TASK_DB

# 启动生产服务
./scripts/start_prod.sh

# 构建前端
cd frontend && npm run build
```

---

## 📖 更多文档

- **详细使用说明**: [scripts/README.md](scripts/README.md)
- **项目开发规范**: [doc/need.md](doc/need.md)
- **Claude设计规范**: [doc/CLAUDE_DESIGN_IMPLEMENTATION.md](doc/CLAUDE_DESIGN_IMPLEMENTATION.md)
- **API文档**: 待完善

---

## 💡 小贴士

1. **首次启动较慢** - 需要安装依赖，请耐心等待
2. **保持终端开启** - 关闭终端会停止服务
3. **查看实时日志** - 后端日志在 `backend/app.log`
4. **热重载** - 代码修改后会自动重启（开发模式）
5. **浏览器缓存** - 前端更新后可能需要强制刷新 (Cmd+Shift+R)

---

## 🆘 获取帮助

如果遇到问题：

1. 查看控制台错误信息
2. 检查 `backend/app.log` 日志文件
3. 参考本文档的"常见问题速查"章节
4. 查看详细文档: [scripts/README.md](scripts/README.md)
5. 提交Issue或联系开发团队

---

**祝您使用愉快！** 🎉
