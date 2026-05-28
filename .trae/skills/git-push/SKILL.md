---
name: "git-push"
description: "Pushes project updates to GitHub repository. Invoke when user says 'push to GitHub', '提交代码', '推送', or asks to sync with the remote repo."
---

# Git Push to GitHub

将该项目的代码更新推送到 GitHub 远程仓库 `https://github.com/pipibigking/luokewangguo-quanzhan`。

## 工作流程

### 1. 检查状态
- 运行 `git status` 查看当前改动列表
- 显示有改动的文件和未跟踪的文件

### 2. 询问用户意见
向用户提问以下内容：
- **提交哪些文件**：让用户从 `git status` 的列表中勾选要提交的文件（可全选）
- **commit message**：让用户填写本次提交的信息
- 注意：`.trae/` 目录下的技能文件需要提醒用户是否一并提交

### 3. 暂存文件
- 执行 `git add <文件路径>` 暂存用户选择的文件
- **需要排除的文件**（永远不要提交）：
  - `*.pyc`、`__pycache__/` 等编译缓存
  - `node_modules/` 等依赖目录
  - `.env` 等环境配置

### 4. 提交
- 执行 `git commit -m "<用户提供的commit message>"`

### 5. 推送到远程
- 执行 `git push origin main` 推送到远程仓库
- 如果推送失败，检查网络连接和权限，提示用户确认 GitHub 认证信息

### 6. 结果反馈
- 推送成功后，告知用户推送完成
- 显示推送的 commit 摘要信息
