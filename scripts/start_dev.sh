#!/bin/bash
# ============================================
# Task Scheduler - 开发环境启动脚本
# 适用于 macOS / Linux
# ============================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Task Scheduler - 开发环境启动"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo -e "${YELLOW}[1/5] 检查环境...${NC}"

# 检查Python虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}创建Python虚拟环境...${NC}"
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到Node.js，请先安装Node.js${NC}"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到npm，请先安装npm${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境检查通过${NC}"
echo ""

echo -e "${YELLOW}[2/5] 初始化数据库（如需要）...${NC}"

# 检查MySQL是否运行
if command -v mysql &> /dev/null; then
    if mysql -u root -p12345678 -e "SELECT 1" &> /dev/null; then
        # 创建数据库（如果不存在）
        mysql -u root -p12345678 -e "CREATE DATABASE IF NOT EXISTS task_scheduler_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
        echo -e "${GREEN}✓ 数据库准备就绪${NC}"
    else
        echo -e "${YELLOW}⚠ MySQL未运行或密码不正确，请手动检查${NC}"
    fi
else
    echo -e "${YELLOW}⚠ 未找到mysql命令，跳过数据库初始化${NC}"
fi

echo ""

echo -e "${YELLOW}[3/5] 安装后端依赖...${NC}"
cd backend

# 检查requirements.txt是否存在
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
else
    echo -e "${YELLOW}⚠ 未找到requirements.txt，跳过依赖安装${NC}"
fi

echo ""

echo -e "${YELLOW}[4/5] 安装前端依赖...${NC}"
cd ../frontend

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ 前端依赖已存在${NC}"
fi

echo ""

echo -e "${YELLOW}[5/5] 启动服务...${NC}"
echo ""
echo -e "${GREEN}=========================================="
echo "  服务启动信息"
echo "==========================================${NC}"
echo -e "${GREEN}后端API: http://localhost:5001${NC}"
echo -e "${GREEN}前端界面: http://localhost:3000${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止所有服务${NC}"
echo ""

# 设置环境变量
export FLASK_ENV=development
export FLASK_PORT=5001
export FLASK_DEBUG=True

# 启动后端（后台运行）
cd ../backend
echo -e "${YELLOW}启动后端服务...${NC}"
python run.py &
BACKEND_PID=$!

# 等待后端启动
sleep 2

# 启动前端
cd ../frontend
echo -e "${YELLOW}启动前端服务...${NC}"
npm run dev &
FRONTEND_PID=$!

# 捕获退出信号
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待进程
wait
