# Python 虚拟环境使用说明

## 环境信息

- **Python版本**: 3.13.3 (3.13.x系列)
- **虚拟环境路径**: `.venv/`
- **位置**: `/Users/linziwang/PycharmProjects/task-scheduler/.venv`

## 激活虚拟环境

### macOS/Linux
```bash
source .venv/bin/activate
```

### Windows
```cmd
.venv\Scripts\activate
```

## 退出虚拟环境

```bash
deactivate
```

## 已安装的主要依赖

| 包名 | 版本 | 用途 |
|------|------|------|
| Flask | 3.0.0 | Web框架 |
| Flask-SQLAlchemy | 3.1.1 | ORM框架 |
| Flask-CORS | 4.0.0 | 跨域支持 |
| SQLAlchemy | 2.0.36 | 数据库ORM |
| PyMySQL | 1.1.0 | MySQL驱动 |
| APScheduler | 3.10.4 | 定时任务调度 |
| Pandas | 2.2.0 | 数据处理 |
| openpyxl | 3.1.2 | Excel导出 |
| cryptography | 41.0.7 | 加密工具 |
| python-dotenv | 1.0.0 | 环境变量管理 |

## 常用命令

### 查看已安装的包
```bash
pip list
```

### 导出依赖清单
```bash
pip freeze > requirements.txt
```

### 安装依赖
```bash
pip install -r backend/requirements.txt
```

### 升级pip
```bash
pip install --upgrade pip
```

## 注意事项

1. **Python版本要求**: 本项目必须使用 Python 3.13.x 系列（当前为3.13.3）
2. **虚拟环境激活**: 每次运行项目前必须先激活虚拟环境
3. **依赖管理**: 所有依赖都已在 `backend/requirements.txt` 中声明
4. **离线部署**: Windows Server离线环境需要从开发机器下载.whl文件后传输

## 启动应用

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 进入后端目录
cd backend

# 3. 启动Flask应用
python run.py
```

应用将在 http://0.0.0.0:5000 启动

## 问题排查

### 问题1: 提示 "No module named 'flask'"
**解决方案**: 确保已激活虚拟环境
```bash
source .venv/bin/activate
```

### 问题2: Python版本不匹配
**解决方案**: 检查Python版本
```bash
python --version  # 应该显示 Python 3.13.3
```

### 问题3: 依赖冲突
**解决方案**: 重新创建虚拟环境
```bash
# 删除旧环境
rm -rf .venv

# 创建新环境
python3.13 -m venv .venv

# 激活并安装依赖
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

**最后更新**: 2026-04-20
