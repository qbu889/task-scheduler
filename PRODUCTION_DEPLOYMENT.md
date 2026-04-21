# 生产环境部署指南 - 达梦数据库驱动安装

## 概述
本系统在生产环境使用达梦 DM8 数据库。由于达梦数据库的 Python 驱动不在 PyPI 上,需要在生产服务器上手动安装。

## 前置条件
- 已在服务器安装达梦 DM8 数据库
- Python 3.10+ 环境
- pip 包管理工具

## 安装步骤

### 1. 定位达梦驱动源码
达梦数据库安装后,驱动源码位于安装目录的 `drivers/python` 文件夹下:
```bash
# 假设达梦安装在 /opt/dmdbms
cd /opt/dmdbms/drivers/python/
ls -l
# 应该看到 dmPython 和 sqlalchemy_dm(或 dmSQLAlchemy) 目录
```

### 2. 安装 dmPython 驱动
```bash
cd /opt/dmdbms/drivers/python/dmPython
python setup.py install
```

### 3. 安装 SQLAlchemy 方言包
根据您使用的 SQLAlchemy 版本选择对应的方言包:

**如果使用 SQLAlchemy 2.0.x (本项目使用):**
```bash
cd /opt/dmdbms/drivers/python/sqlalchemy_dm/dmSQLAlchemy2.0
python setup.py install
```

**如果使用 SQLAlchemy 1.4.x:**
```bash
cd /opt/dmdbms/drivers/python/sqlalchemy_dm
python setup.py install
```

### 4. 验证安装
```bash
python -c "import dmPython; print('dmPython version:', dmPython.__version__)"
python -c "import sqlalchemy_dm; print('sqlalchemy_dm installed successfully')"
```

### 5. 配置环境变量
确保已设置以下环境变量(在 `.env.production` 文件中):
```bash
DM_HOST=your_dm_host
DM_USER=SYSDBA
DM_PASSWORD=your_password
DM_DATABASE=TASK_DB
DM_PORT=5236
```

### 6. 安装其他依赖
```bash
cd /path/to/task-scheduler/backend
pip install -r requirements.txt
```

### 7. 启动服务
```bash
cd /path/to/task-scheduler
./scripts/start_prod.sh
```

## 常见问题

### 问题1: 编译失败 - 缺少头文件
**错误信息**: `fatal error: dpi.h: No such file or directory`

**解决方案**: 设置 DM_HOME 环境变量
```bash
export DM_HOME=/opt/dmdbms
export LD_LIBRARY_PATH=$DM_HOME/bin:$LD_LIBRARY_PATH
```

### 问题2: ImportError: No module named 'sqlalchemy_dm'
**原因**: 未安装 SQLAlchemy 方言包或版本不匹配

**解决方案**: 
- 确认已安装对应版本的 sqlalchemy_dm
- SQLAlchemy 2.0.x 需要使用 dmSQLAlchemy2.0 目录下的源码

### 问题3: 运行时找不到动态库
**错误信息**: `libdmdpi.so: cannot open shared object file`

**解决方案**:
```bash
# 添加到达梦库文件的搜索路径
echo "/opt/dmdbms/bin" > /etc/ld.so.conf.d/dm.conf
ldconfig
```

## 版本兼容性

| SQLAlchemy 版本 | sqlalchemy_dm 版本 | 说明 |
|----------------|-------------------|------|
| 1.3.x | 1.1.10 | 旧版本 |
| 1.4.x | 1.4.39 | 稳定版本 |
| 2.0.x | 2.0.0+ | **本项目使用** |

## 离线安装(无网络环境)

如果生产服务器无法访问互联网:

1. **在有网络的机器上下载依赖**:
```bash
pip download -d ./wheels -r requirements.txt
```

2. **打包达梦驱动**:
```bash
tar -czf dm-drivers.tar.gz /opt/dmdbms/drivers/python/
```

3. **传输到生产服务器并安装**:
```bash
# 安装 Python 依赖
pip install --no-index --find-links=./wheels -r requirements.txt

# 安装达梦驱动
tar -xzf dm-drivers.tar.gz
cd python/dmPython && python setup.py install
cd ../sqlalchemy_dm/dmSQLAlchemy2.0 && python setup.py install
```

## 参考文档
- 达梦官方文档: https://eco.dameng.com/document/dm/zh-cn/app-dev/python-SQLAlchemy.html
- dmPython 安装指南: https://eco.dameng.com/document/dm/zh-cn/pm/dmpython-installation.html
