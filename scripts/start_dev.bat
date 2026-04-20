@echo off
REM ============================================
REM Task Scheduler - 开发环境启动脚本
REM 适用于 Windows
REM ============================================

chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   Task Scheduler - 开发环境启动
echo ==========================================
echo.

REM 检查项目根目录
cd /d "%~dp0.."

echo [1/5] 检查环境...

REM 检查Python虚拟环境
if not exist ".venv" (
    echo 创建Python虚拟环境...
    python -m venv .venv
)

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 检查Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 检查npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误: 未找到npm，请先安装npm
    pause
    exit /b 1
)

echo ✓ 环境检查通过
echo.

echo [2/5] 初始化数据库（如需要）...

REM 检查MySQL是否运行
where mysql >nul 2>nul
if %errorlevel% equ 0 (
    mysql -u root -p12345678 -e "SELECT 1" >nul 2>nul
    if !errorlevel! equ 0 (
        REM 创建数据库（如果不存在）
        mysql -u root -p12345678 -e "CREATE DATABASE IF NOT EXISTS task_scheduler_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>nul
        echo ✓ 数据库准备就绪
    ) else (
        echo ⚠ MySQL未运行或密码不正确，请手动检查
    )
) else (
    echo ⚠ 未找到mysql命令，跳过数据库初始化
)

echo.

echo [3/5] 安装后端依赖...
cd backend

REM 检查requirements.txt是否存在
if exist "requirements.txt" (
    pip install -r requirements.txt -q
    echo ✓ 后端依赖安装完成
) else (
    echo ⚠ 未找到requirements.txt，跳过依赖安装
)

echo.

echo [4/5] 安装前端依赖...
cd ..\frontend

REM 检查node_modules是否存在
if not exist "node_modules" (
    call npm install
    echo ✓ 前端依赖安装完成
) else (
    echo ✓ 前端依赖已存在
)

echo.

echo [5/5] 启动服务...
echo.
echo ==========================================
echo   服务启动信息
echo ==========================================
echo 后端API: http://localhost:5001
echo 前端界面: http://localhost:3000
echo ==========================================
echo.
echo 提示: 按 Ctrl+C 停止所有服务
echo.

REM 设置环境变量
set FLASK_ENV=development
set FLASK_PORT=5001
set FLASK_DEBUG=True

REM 启动后端（新窗口）
cd ..\backend
start "Task Scheduler - Backend" cmd /k "python run.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端（新窗口）
cd ..\frontend
start "Task Scheduler - Frontend" cmd /k "npm run dev"

echo.
echo ✓ 服务已在新窗口中启动
echo.
pause
