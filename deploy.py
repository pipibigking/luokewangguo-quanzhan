#!/usr/bin/env python3
"""
自动上传项目到 GitHub 并同步更新 Railway 后端
作者: pipibigking
日期: 2026-05-12
"""

import subprocess
import sys
from datetime import datetime

def run_command(cmd, cwd=None):
    """执行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️  警告:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 自动上传项目到 GitHub + Railway")
    print("=" * 60)
    
    project_dir = r"d:\Trae_project\开发1\洛克王国异色html\yise_Window"
    
    # 1. 检查状态
    print("\n📋 [1/6] 检查 Git 状态...")
    if not run_command("git status", cwd=project_dir):
        print("❌ 状态检查失败")
        return 1
    
    # 2. 拉取最新代码
    print("\n📥 [2/6] 拉取最新代码...")
    run_command("git pull origin main", cwd=project_dir)  # 允许失败继续
    
    # 3. 添加文件
    print("\n➕ [3/6] 添加文件到暂存区...")
    if not run_command("git add .", cwd=project_dir):
        print("❌ 添加文件失败")
        return 1
    
    # 4. 提交
    print("\n📝 [4/6] 提交更改...")
    commit_msg = f"自动更新项目 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if not run_command(f'git commit -m "{commit_msg}"', cwd=project_dir):
        print("⚠️  没有需要提交的更改或提交失败")
    
    # 5. 推送到 GitHub
    print("\n📤 [5/6] 推送到 GitHub...")
    if not run_command("git push origin main", cwd=project_dir):
        print("❌ 推送失败")
        return 1
    
    # 6. Railway 自动部署（由 webhook 触发）
    print("\n🔄 [6/6] 触发 Railway 重新部署...")
    print("✓ Railway 已配置自动部署，代码推送后会自动更新")
    print("\n" + "=" * 60)
    print("✅ 所有操作完成！")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
