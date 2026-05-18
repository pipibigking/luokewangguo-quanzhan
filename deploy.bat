@echo off
chcp 65001 >nul
title 洛克王国异色精灵展示系统 - 部署

echo ============================================
echo   洛克王国异色精灵展示系统 - 一键部署
echo ============================================
echo.

:: 进入项目根目录
cd /d "%~dp0"

:: 清理旧进程
echo [0/4] 清理旧进程...
taskkill /f /im python.exe >nul 2>nul
taskkill /f /im node.exe >nul 2>nul
timeout /t 2 /nobreak >nul
echo 完成
echo.

:: 第一步：安装后端依赖
echo [1/4] 安装后端依赖...
cd backend
pip install -r requirements.txt -q
cd ..
echo 完成
echo.

:: 第二步：构建前端
echo [2/4] 构建前端项目...
cd frontend
call npm install --legacy-peer-deps --silent
call npx vite build
cd ..
echo 完成
echo.

:: 第三步：启动后端（同时提供前端页面和API）
echo [3/4] 启动服务...
echo.
echo ============================================
echo  服务启动中，请稍候...
echo  访问地址: http://localhost:8004/
echo  后台管理: http://localhost:8004/#/admin
echo  API文档:  http://localhost:8004/docs
echo ============================================
echo.

cd backend
python main.py

pause
