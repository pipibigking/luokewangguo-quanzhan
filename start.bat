@echo off
chcp 65001 >nul
title 洛克王国异色精灵展示系统

echo ========================================
echo   洛克王国异色精灵展示系统 - 启动中
echo ========================================
echo.

REM 进入项目目录
cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [1/3] 检查依赖...
cd backend
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 首次运行，正在安装依赖...
    pip install -r requirements.txt
)
cd ..

echo.
echo [2/3] 启动服务...
echo.
echo ========================================
echo   服务启动成功！
echo   请在浏览器中打开:
echo   http://localhost:8004
echo.
echo   按 Ctrl+C 可以停止服务
echo ========================================
echo.

cd backend
python main.py

pause
