# ==========================================
# 后端依赖离线打包脚本 (PowerShell)
# 在有网络的 Windows 开发机上执行
# ==========================================

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Task Scheduler 后端依赖离线打包" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# 进入 backend 目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "..\backend"
Set-Location $backendDir

# 创建离线包目录
$packagesDir = Join-Path $backendDir "offline_packages"
if (-not (Test-Path $packagesDir)) {
    New-Item -ItemType Directory -Path $packagesDir | Out-Null
    Write-Host "创建离线包目录: $packagesDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[1/2] 下载所有 Python 依赖包..." -ForegroundColor Cyan
pip download -r requirements.txt -d $packagesDir

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "错误：下载失败，请检查网络连接" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "[2/2] 统计离线包信息..." -ForegroundColor Cyan
Write-Host ""

# 统计文件数量和大小
$files = Get-ChildItem -Path $packagesDir -Recurse -File
$count = $files.Count
$totalSize = ($files | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($totalSize / 1MB, 2)

Write-Host "成功下载 $count 个离线依赖包" -ForegroundColor Green
Write-Host "目录: backend\offline_packages"
Write-Host "总大小: $sizeMB MB" -ForegroundColor Yellow

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "离线包准备完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1. 前端构建：" -NoNewline
Write-Host " cd ..\frontend && npm install && npm run build" -ForegroundColor Yellow
Write-Host "2. 整个项目打包传输到目标服务器"
Write-Host "3. 在目标服务器运行 " -NoNewline
Write-Host "scripts\install_backend.bat" -ForegroundColor Yellow
Write-Host ""

Read-Host "按回车键退出"
