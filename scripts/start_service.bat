@echo off
REM ==========================================
REM 启动服务脚本（Windows）
REM ==========================================

setlocal enabledelayedexpansion

echo ==========================================
echo 启动 Task Scheduler 服务
echo ==========================================
echo.

cd /d %~dp0..
cd backend

REM 检查虚拟环境
if not exist venv (
    echo 错误：虚拟环境不存在
    echo 请先运行 scripts\install_backend.bat 安装依赖
    pause
    exit /b 1
)

REM 检查环境配置文件
if not exist .env.production (
    echo 警告：.env.production 文件不存在
    echo 将使用默认配置
    echo.
)

REM 激活虚拟环境并启动
echo [1/2] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [2/2] 启动 Flask 应用...
echo.
echo 访问地址：http://localhost:5000
echo 按 Ctrl+C 停止服务
echo.

python run.py

pause
