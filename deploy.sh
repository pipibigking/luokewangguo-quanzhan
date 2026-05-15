#!/bin/bash
set -e

echo "============================================="
echo "  洛克王国异色精灵展示系统 - CentOS 7.9 一键部署"
echo "============================================="
echo ""

cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo "[1/6] 安装系统依赖..."
echo "正在安装 Python 3、Node.js 18 和 Git..."

if ! command -v python3 &> /dev/null; then
    sudo yum install -y python3 python3-pip
fi

if ! command -v node &> /dev/null; then
    sudo yum install -y epel-release
    curl -sL https://rpm.nodesource.com/setup_18.x | sudo bash -
    sudo yum install -y nodejs
fi

if ! command -v git &> /dev/null; then
    sudo yum install -y git
fi

echo "系统依赖安装完成"
echo ""

echo "[2/6] 配置防火墙..."
sudo firewall-cmd --zone=public --add-port=8004/tcp --permanent
sudo firewall-cmd --reload
echo "防火墙配置完成 (已开放端口 8004)"
echo ""

echo "[3/6] 安装后端依赖..."
cd backend
if [ ! -d "__pycache__" ]; then
    pip3 install -r requirements.txt -q
fi
cd ..
echo "后端依赖安装完成"
echo ""

echo "[4/6] 构建前端项目..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi
npm run build
cd ..
echo "前端构建完成"
echo ""

echo "[5/6] 清理旧进程..."
pkill -f "uvicorn" || true
pkill -f "python3 main.py" || true
sleep 2
echo "旧进程清理完成"
echo ""

echo "[6/6] 启动服务..."
echo ""
echo "============================================="
echo "  服务启动中，请稍候..."
echo "  访问地址: http://服务器IP:8004/"
echo "  后台管理: http://服务器IP:8004/#/admin"
echo "  API文档:  http://服务器IP:8004/docs"
echo "  默认管理员: admin / admin123"
echo "============================================="
echo ""

cd backend
nohup python3 main.py > app.log 2>&1 &
sleep 3

if grep -q "Application startup complete" app.log; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "查看日志: tail -f backend/app.log"
    echo "停止服务: pkill -f 'python3 main.py'"
else
    echo "❌ 服务启动失败，请查看日志:"
    cat app.log
    exit 1
fi