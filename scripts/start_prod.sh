#!/bin/bash
# ============================================
# Task Scheduler - 生产环境启动脚本
# 适用于 macOS / Linux
# ============================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Task Scheduler - 生产环境启动"
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

echo -e "${YELLOW}[1/4] 检查环境变量...${NC}"

# 加载生产环境配置文件
ENV_FILE="$PROJECT_ROOT/backend/.env.production"
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}✓ 找到环境配置文件: $ENV_FILE${NC}"
    # 导出所有环境变量(排除注释行和空行)
    set -a
    source "$ENV_FILE"
    set +a
else
    echo -e "${RED}错误: 未找到环境配置文件 $ENV_FILE${NC}"
    exit 1
fi

# 检查必需的环境变量
if [ -z "$DM_HOST" ]; then
    echo -e "${RED}错误: 未设置 DM_HOST 环境变量${NC}"
    echo -e "${YELLOW}请在 backend/.env.production 中设置以下配置:${NC}"
    echo "  DM_HOST=your_dm_host"
    echo "  DM_USER=SYSDBA"
    echo "  DM_PASSWORD=your_password"
    echo "  DM_DATABASE=TASK_DB"
    exit 1
fi

if [ -z "$DM_USER" ]; then
    echo -e "${RED}错误: 未设置 DM_USER 环境变量${NC}"
    exit 1
fi

if [ -z "$DM_PASSWORD" ]; then
    echo -e "${RED}错误: 未设置 DM_PASSWORD 环境变量${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 环境变量检查通过${NC}"
echo ""

echo -e "${YELLOW}[2/4] 激活Python虚拟环境...${NC}"

# 检查Python虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${RED}错误: 未找到虚拟环境 .venv${NC}"
    echo -e "${YELLOW}请先运行开发环境脚本或手动创建虚拟环境${NC}"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate
echo -e "${GREEN}✓ 虚拟环境已激活${NC}"
echo ""

echo -e "${YELLOW}[3/4] 检查后端依赖...${NC}"
cd backend

# 检查requirements.txt是否存在
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
    echo -e "${GREEN}✓ 后端依赖检查完成${NC}"
else
    echo -e "${RED}错误: 未找到requirements.txt${NC}"
    exit 1
fi

echo ""

echo -e "${YELLOW}[4/4] 启动生产服务...${NC}"
echo ""
echo -e "${GREEN}=========================================="
echo "  生产环境配置"
echo "==========================================${NC}"
echo -e "${GREEN}数据库类型: 达梦数据库 (DM8)${NC}"
echo -e "${GREEN}数据库主机: ${DM_HOST}${NC}"
echo -e "${GREEN}数据库用户: ${DM_USER}${NC}"
echo -e "${GREEN}后端端口: 5000${NC}"
echo -e "${GREEN}调试模式: 关闭${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo -e "${YELLOW}提示: 按 Ctrl+C 停止服务${NC}"
echo ""

# 设置生产环境变量
export FLASK_ENV=production
export FLASK_PORT=5000
export FLASK_DEBUG=False

# 启动后端
echo -e "${YELLOW}启动后端服务...${NC}"
python run.py
