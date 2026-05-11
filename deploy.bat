@echo off
REM 自动上传项目到 GitHub + Railway
REM 作者: pipibigking
REM 日期: 2026-05-12

echo.
echo ============================================================
echo   🚀  自动上传项目到 GitHub + Railway
echo ============================================================
echo.

cd /d "d:\Trae_project\开发1\洛克王国异色html\yise_Window"

REM 1. 检查状态
echo [1/6] 📋 检查 Git 状态...
git status
if errorlevel 1 (
    echo ❌ Git 状态检查失败
    pause
    exit /b 1
)
echo.

REM 2. 拉取最新代码
echo [2/6] 📥 拉取最新代码...
git pull origin main
echo.

REM 3. 添加文件
echo [3/6] ➕ 添加文件到暂存区...
git add .
if errorlevel 1 (
    echo ❌ 添加文件失败
    pause
    exit /b 1
)
echo.

REM 4. 提交
echo [4/6] 📝 提交更改...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "MI=%dt:~10,2%"
set "SS=%dt:~12,2%"
git commit -m "自动更新项目 - %YYYY%-%MM%-%DD% %HH%:%MI%:%SS%"
if errorlevel 1 (
    echo ⚠️  没有需要提交的更改或提交失败
)
echo.

REM 5. 推送到 GitHub
echo [5/6] 📤 推送到 GitHub...
git push origin main
if errorlevel 1 (
    echo ❌ 推送失败
    pause
    exit /b 1
)
echo.

REM 6. Railway 自动部署
echo [6/6] 🔄 触发 Railway 重新部署...
echo ✓ Railway 已配置自动部署，代码推送后会自动更新
echo.

echo ============================================================
echo   ✅  所有操作完成！
echo ============================================================
echo.
pause
