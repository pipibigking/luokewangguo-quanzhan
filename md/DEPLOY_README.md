# 🚀 自动部署工具使用说明

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `deploy.py` | Python 版本部署脚本（跨平台） |
| `deploy.bat` | Windows 批处理版本（双击运行） |
| `skills/upload_to_github.skill` | Skill 技能文件 |

## 🎯 使用方法

### 方法 1：Windows 双击使用（推荐）
1. 找到 `deploy.bat` 文件
2. 双击运行即可！

### 方法 2：Python 脚本使用
```bash
cd d:\Trae_project\开发1\洛克王国异色html\yise_Window
python deploy.py
```

## 📝 执行流程

```
1. 检查 Git 状态
   ↓
2. 拉取最新代码
   ↓
3. 添加所有更改
   ↓
4. 自动提交（带时间戳）
   ↓
5. 推送到 GitHub
   ↓
6. Railway 自动部署（由 GitHub webhook 触发）
```

## ⚙️ 前置条件

- ✅ 已配置 Git 账号
- ✅ 已关联 GitHub 仓库
- ✅ Railway 已连接到 GitHub（自动部署）

## 📌 注意事项

1. 确保当前在正确的项目目录
2. 确保有网络连接
3. 如果需要修改提交信息，编辑脚本中的 `commit -m` 部分
