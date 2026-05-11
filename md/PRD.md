# 洛克王国精灵展示界面 - 产品需求文档

## 一、引言

本项目旨在构建一个洛克王国异色精灵展示平台，为用户提供浏览、搜索、筛选和查看精灵详情的完整体验。

## 二、目标

- 建立完整的精灵数据管理系统，支持19+只异色精灵的展示
- 提供流畅的用户交互体验，包含卡片浏览、详情查看、前后切换等功能
- 支持多维度筛选和搜索，提升用户查找效率

## 三、技术架构

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue3 + Vite + TypeScript + TailwindCSS | 现代化前端框架，类型安全，样式快速开发 |
| 后端 | Python (FastAPI) | 高性能API框架，异步支持，自动生成文档 |
| 数据库 | SQLite | 轻量级数据库，无需安装，直接使用文件存储 |
| 缓存 | Redis | 缓存精灵列表，提升查询性能 |

## 四、数据模型设计

### 精灵表 (pets)

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| id | INT | 主键ID | AUTO_INCREMENT, PRIMARY KEY |
| name | VARCHAR(50) | 精灵名称 | NOT NULL |
| group | VARCHAR(50) | 分组类型 | NOT NULL |
| image_url | VARCHAR(255) | 图片路径 | NOT NULL |
| price | INT | 价格 | NOT NULL |
| attributes | TEXT (JSON) | 属性数组（支持多属性） | 默认空数组 |
| description | TEXT | 精灵描述（长文本） | 默认空字符串 |
| created_at | DATETIME | 创建时间 | DEFAULT CURRENT_TIMESTAMP |

### 分组枚举值
- 赛季异色
- 赛季奇遇异色
- 赛季战令异色
- 活动异色

## 五、功能需求

### 1. 精灵列表展示
- 以卡片形式展示精灵列表
- 每张卡片显示：精灵图片、名称、分组标签、价格
- 卡片hover时有缩放效果

### 2. 筛选功能
- 按分组筛选（赛季异色/赛季奇遇异色/赛季战令异色/活动异色）
- 支持"全部"选项

### 3. 搜索功能
- 按精灵名称模糊搜索
- 搜索与筛选可组合使用

### 4. 排序功能
- 价格升序排序
- 价格降序排序

### 5. 详情查看
- 点击卡片打开详情弹窗/页面
- 详情包含：大图、名称、分组、属性标签、价格、描述

### 6. 详情切换
- 在详情窗口内支持"上一个"/"下一个"切换
- 切换时有淡入淡出动画效果
- 循环切换（最后一个的下一个是第一个）

## 六、API接口设计

### 1. 获取精灵列表
- **路径**: `/api/pets`
- **方法**: GET
- **参数**:
  - `group`: 分组筛选（可选）
  - `search`: 搜索关键词（可选）
  - `sort_by`: 排序字段（默认id）
  - `sort_order`: 排序方向（asc/desc，默认asc）
- **响应**: 精灵列表数组

### 2. 获取单个精灵
- **路径**: `/api/pets/{id}`
- **方法**: GET
- **响应**: 单个精灵详情

### 3. 获取分组列表
- **路径**: `/api/groups`
- **方法**: GET
- **响应**: 分组名称数组

## 七、环境配置清单

### 1. Redis（缓存）
- **推荐版本**: Redis 7.0+
- **用途**: 缓存精灵列表，减少数据库查询压力

### 2. Python（后端）
- **推荐版本**: Python 3.10+
- **需要安装的依赖**:
  - fastapi
  - uvicorn（ASGI服务器）
  - sqlalchemy（ORM）
  - redis（Redis客户端）
  - python-dotenv（环境变量）

### 3. Node.js（前端）
- **推荐版本**: Node.js 18+
- **需要安装的依赖**:
  - Vue3 + Vite
  - TypeScript
  - TailwindCSS 3
  - axios（HTTP客户端）

## 八、项目结构

```
yise_Window/
├── backend/
│   ├── .env              # 环境变量配置
│   ├── main.py           # FastAPI 主程序
│   ├── init_db.py        # 数据库初始化脚本
│   └── requirements.txt  # Python 依赖
├── frontend/             # Vue3 前端项目
│   ├── src/
│   │   ├── components/   # Vue 组件
│   │   ├── api/          # API 调用
│   │   ├── types/        # TypeScript 类型
│   │   └── App.vue       # 主组件
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── images/               # 精灵图片
├── pets.js              # 原有数据文件
└── PRD.md               # 产品需求文档
```

## 九、待办事项

- [ ] 安装 Redis 7.0+（如不使用缓存可跳过）
- [ ] 安装 Python 3.10+ 及依赖包
- [ ] 安装 Node.js 18+
- [ ] 初始化 SQLite 数据库
- [ ] 开发 FastAPI 后端接口
- [ ] 开发 Vue3 前端界面
- [ ] 配置 Redis 缓存（如需要）
- [ ] 部署测试