@echo off
REM ============================================
REM Task Scheduler - 生产环境启动脚本
REM 适用于 Windows
REM ============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   Task Scheduler - 生产环境启动
echo ==========================================
echo.

REM 检查项目根目录
cd /d "%~dp0.."

echo [1/4] 检查环境变量...

REM 检查必需的环境变量
if "%DM_HOST%"=="" (
    echo 错误: 未设置 DM_HOST 环境变量
    echo 请设置以下环境变量:
    echo   set DM_HOST=your_dm_host
    echo   set DM_USER=SYSDBA
    echo   set DM_PASSWORD=your_password
    echo   set DM_DATABASE=TASK_DB
    pause
    exit /b 1
)

if "%DM_USER%"=="" (
    echo 错误: 未设置 DM_USER 环境变量
    pause
    exit /b 1
)

if "%DM_PASSWORD%"=="" (
    echo 错误: 未设置 DM_PASSWORD 环境变量
    pause
    exit /b 1
)

echo ✓ 环境变量检查通过
echo.

echo [2/4] 激活Python虚拟环境...

REM 检查Python虚拟环境
if not exist ".venv" (
    echo 错误: 未找到虚拟环境 .venv
    echo 请先运行开发环境脚本或手动创建虚拟环境
    pause
    exit /b 1
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat
echo ✓ 虚拟环境已激活
echo.

echo [3/4] 检查后端依赖...
cd backend

REM 检查requirements.txt是否存在
if exist "requirements.txt" (
    pip install -r requirements.txt -q
    echo ✓ 后端依赖检查完成
) else (
    echo 错误: 未找到requirements.txt
    pause
    exit /b 1
)

echo.

echo [4/4] 启动生产服务...
echo.
echo ==========================================
echo   生产环境配置
echo ==========================================
echo 数据库类型: 达梦数据库 (DM8)
echo 数据库主机: %DM_HOST%
echo 数据库用户: %DM_USER%
echo 后端端口: 5000
echo 调试模式: 关闭
echo ==========================================
echo.
echo 提示: 按 Ctrl+C 停止服务
echo.

REM 设置生产环境变量
set FLASK_ENV=production
set FLASK_PORT=5000
set FLASK_DEBUG=False

REM 启动后端
echo 启动后端服务...
python run.py
