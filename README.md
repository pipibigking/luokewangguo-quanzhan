
# 🎉 洛克王国异色精灵交易平台 (LuokeQuanzhan)

一个基于 Vue 3 + FastAPI + SQLite 的全栈洛克王国异色精灵展示与管理平台，支持前台展示与后台管理功能。

---

## 📸 功能特性

### 🖥️ 前台用户端
- 🎨 美观的精灵卡片展示与筛选
- 🏷️ 按属性、组别、状态筛选
- 🔍 精灵详情弹窗查看
- 📌 滚动公告栏
- 🎭 分组颜色自定义

### 🔧 后台管理端
- ✨ 精灵增删改查
- 📤/📥 一键批量上架/下架
- 📝 精灵特点编辑
- 🏷️ 分组颜色管理
- 📢 公告管理
- 👤 账号管理
- 🔐 管理员登录

---

## 🛠️ 技术栈

| 层级 | 技术 |
|---|---|
| **前端** | Vue 3 (Composition API) + TypeScript + Vite + Tailwind CSS |
| **后端** | FastAPI (Python 3) + SQLite (SQLAlchemy) |
| **数据库** | SQLite |

---

## 📂 项目结构

```
yise_Window/
├── backend/                  # 后端目录
│   ├── main.py               # FastAPI 主服务 (端口 8004)
│   ├── init_db.py            # 数据库初始化脚本
│   ├── requirements.txt      # Python 依赖
│   ├── locke_pets.db         # 数据库 (git 忽略)
│   └── .env                  # 环境配置 (git 忽略)
├── frontend/                 # 前端目录
│   ├── src/
│   │   ├── api/              # API 封装
│   │   ├── components/       # Vue 组件
│   │   ├── pages/            # 页面组件
│   │   ├── router/           # Vue Router
│   │   ├── types/            # TypeScript 类型定义
│   │   └── utils/            # 工具函数
│   ├── dist/                 # 构建产物 (git 忽略)
│   ├── vite.config.ts        # Vite 配置
│   └── package.json
├── images/                   # 精灵图片资源
├── wiki_style_icons/         # 属性 SVG 图标
└── md/                       # 项目文档
```

---

## 🚀 快速开始

### 前置条件
- Python 3.8+
- Node.js 16+ (推荐 LTS)
- npm 或 pnpm

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 初始化数据库（首次运行）

```bash
cd backend
python init_db.py
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

后端将运行在 **`http://localhost:8004`**

### 4. 安装前端依赖并启动

```bash
cd frontend
npm install
npm run dev
```

前端将运行在 **`http://localhost:5173`**

### 5. 默认管理员账号

| 用户名 | 密码 |
|---|---|
| `admin` | `admin123` |

后台入口：**`http://localhost:5173/admin/login`**

---

## 📝 接口文档

后端启动后，访问 **`http://localhost:8004/docs`** 查看 Swagger API 文档。

主要 API：

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/pets` | 获取精灵列表 |
| `GET` | `/api/pets/{id}` | 获取单个精灵详情 |
| `POST` | `/api/pets` | 新增精灵 |
| `PUT` | `/api/pets/{id}` | 更新精灵 |
| `DELETE` | `/api/pets/{id}` | 删除精灵 |
| `PATCH` | `/api/pets/{id}/toggle-active` | 单个上下架 |
| `PATCH` | `/api/pets/batch-activate` | 一键上架 |
| `PATCH` | `/api/pets/batch-deactivate` | 一键下架 |
| `GET` | `/api/group-colors` | 获取分组颜色 |
| `PUT` | `/api/group-colors/{group}` | 保存分组颜色 |
| `GET` | `/api/announcement` | 获取公告 |
| `PUT` | `/api/announcement` | 更新公告 |

---

## 🎨 开发说明

### 前端代理配置
在 `vite.config.ts` 中，默认代理设置：
- `/api` → `http://localhost:8004`
- `/images` → `http://localhost:8004`
- `/icons` → `http://localhost:8004`

### 后端自动迁移
`main.py` 启动时会自动执行 `auto_migrate()`，检测并创建缺失的表和列。

---

## 📄 License

MIT License

---

## 📮 作者

pipibigking

