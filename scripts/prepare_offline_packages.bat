@echo off
REM ==========================================
REM 后端依赖离线打包脚本
REM 在有网络的开发机上执行此脚本
REM ==========================================

echo ==========================================
echo Task Scheduler 后端依赖离线打包
echo ==========================================
echo.

cd backend

REM 创建离线包目录
if not exist offline_packages (
    mkdir offline_packages
)

echo [1/2] 下载所有 Python 依赖包...
pip download -r requirements.txt -d offline_packages

if %errorlevel% neq 0 (
    echo.
    echo 错误：下载失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo [2/2] 统计离线包信息...
echo.
setlocal enabledelayedexpansion

REM 统计文件数量
set count=0
for %%f in (offline_packages\*) do (
    set /a count+=1
)

echo 成功下载 !count! 个离线依赖包
echo 目录：backend\offline_packages
echo.

REM 统计总大小
powershell -Command "Write-Host '总大小:' -NoNewline; (Get-ChildItem -Path 'offline_packages' -Recurse -File | Measure-Object -Property Length -Sum | Select-Object -ExpandProperty Sum | ForEach-Object { '{0:N2} MB' -f ($_ / 1MB) })"

echo.
echo ==========================================
echo 离线包准备完成！
echo ==========================================
echo.
echo 下一步：
echo 1. 前端构建：cd frontend ^&^& npm install ^&^& npm run build
echo 2. 整个项目打包传输到目标服务器
echo 3. 在目标服务器运行 scripts\install_backend.bat
echo.

pause
