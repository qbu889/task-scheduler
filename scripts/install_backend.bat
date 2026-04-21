@echo off
REM ==========================================
REM 后端依赖安装脚本（Windows 离线模式）
REM ==========================================

setlocal enabledelayedexpansion

echo ==========================================
echo Task Scheduler 后端依赖安装（离线模式）
echo ==========================================
echo.

REM 检查 Python
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误：未找到 Python，请先安装 Python 3.10+
    echo 下载地址：https://www.python.org/downloads/windows/
    pause
    exit /b 1
)

python --version
echo.

REM 创建虚拟环境
echo [2/4] 创建虚拟环境...
if exist venv (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo 错误：虚拟环境创建失败
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)
echo.

REM 检查离线包
echo [3/4] 检查离线依赖包...
if not exist offline_packages (
    echo 警告：offline_packages 文件夹不存在
    echo 请先在有网络的机器上执行：pip download -r requirements.txt -d ./offline_packages
    echo.
    set /p choice="是否继续尝试从 PyPI 下载？(y/n): "
    if /i "!choice!"=="y" (
        venv\Scripts\pip install -r requirements.txt
    ) else (
        echo 取消安装
        pause
        exit /b 0
    )
) else (
    echo 离线包目录已找到，开始安装...
    echo.
    venv\Scripts\pip install --no-index --find-links=offline_packages -r requirements.txt
)

if %errorlevel% neq 0 (
    echo.
    echo 错误：依赖安装失败
    pause
    exit /b 1
)

echo.

REM 初始化数据库
echo [4/4] 初始化数据库...
echo.
echo 注意：请确保已配置 .env.production 文件
echo 并创建了对应的数据库
echo.

venv\Scripts\python -c "from app import db, create_app; app = create_app('production'); app.app_context().push(); db.create_all(); print('数据库初始化完成！')"

if %errorlevel% neq 0 (
    echo.
    echo 警告：数据库初始化可能失败，请手动检查
    echo 或稍后运行：venv\Scripts\python -c "from app import db, create_app; ..."
)

echo.
echo ==========================================
echo 后端依赖安装完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 编辑 backend\.env.production 配置环境变量
echo 2. 运行 scripts\start_service.bat 启动服务
echo.

pause
