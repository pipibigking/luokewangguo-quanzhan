# 🎉 洛克王国异色精灵交易平台 (LuokeWangGuo-Quanzhan)

一个基于 **Vue 3 + TypeScript + FastAPI + SQLite** 的全栈洛克王国异色精灵展示与管理平台，支持前台展示与后台管理功能。

---

## 📸 功能特性

### 🖥️ 前台用户端
- 🎨 美观的精灵卡片瀑布流展示
- 🏷️ 按属性、组别筛选精灵
- 🔍 关键词搜索精灵名称
- 📊 价格排序（升序/降序）
- 📋 精灵详情弹窗（属性、技能、描述）
- 📌 顶部滚动公告栏
- 🎭 分组颜色自定义展示
- 💬 留言板功能（支持角色头像选择）

### 🔧 后台管理端
- ✨ 精灵增删改查（支持内联编辑价格）
- 📤/📥 一键批量上架/下架精灵
- 📝 精灵描述与技能编辑
- 🏷️ 分组颜色管理
- 📢 系统公告管理
- 💬 留言管理（查看、标记已读、删除）
- 👤 管理员账号管理（增删改）
- 🔐 管理员登录验证与路由守卫
- 🎨 **各管理页面独立主题背景图**

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|---|---|---|
| **前端框架** | Vue 3 | 3.3.13 |
| **语言** | TypeScript | 5.3.3 |
| **构建工具** | Vite | 5.4.21 |
| **CSS 框架** | Tailwind CSS | 3.4.1 |
| **路由** | Vue Router | 4.6.4 |
| **HTTP 客户端** | Axios | 1.6.2 |
| **动画库** | Anime.js | 3.2.2 |
| **后端框架** | FastAPI | 0.104.1 |
| **数据库** | SQLite + SQLAlchemy | 2.0.31 |

---

## 📂 项目结构

```
yise_Window/
├── backend/                  # 后端目录
│   ├── main.py               # FastAPI 主服务入口
│   ├── init_db.py            # 数据库初始化脚本
│   ├── requirements.txt      # Python 依赖列表
│   ├── system_data.db        # SQLite 数据库文件
│   └── .env                  # 环境配置文件
├── frontend/                 # 前端目录
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── components/       # Vue 组件
│   │   ├── pages/            # 页面组件
│   │   ├── router/           # Vue Router 配置
│   │   ├── types/            # TypeScript 类型定义
│   │   └── utils/            # 工具函数
│   ├── index.html            # HTML 入口
│   ├── package.json          # Node 依赖配置
│   ├── vite.config.ts        # Vite 构建配置
│   ├── tailwind.config.js    # Tailwind CSS 配置
│   └── tsconfig.json         # TypeScript 配置
├── images/                   # 静态图片资源
│   ├── attribute/            # 属性图标 (18种)
│   ├── avatar/               # 留言板角色头像
│   ├── balls/                # 捕捉球图标 (14种)
│   ├── bg/                   # 背景图片（各管理页面主题）
│   ├── pets/                 # 精灵图片 (21种)
│   └── petking/              # 精灵王图片
├── md/                       # 项目文档
└── README.md                 # 项目说明
```

---

## 🚀 快速开始

### 前置条件
- Python 3.8+
- Node.js 16+ (推荐 LTS 版本)
- npm 或 pnpm

### 1. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
cd backend
python main.py
```

后端服务将运行在 **`http://localhost:8004`**

### 3. 安装前端依赖

```bash
cd frontend
npm install
```

### 4. 启动前端开发服务器

```bash
cd frontend
npm run dev
```

前端将运行在 **`http://localhost:5173`**

### 5. 默认管理员账号

| 用户名 | 密码 |
|---|---|
| `admin` | `admin123` |

后台管理入口：**`http://localhost:5173/#/login`**

---

## 📝 接口文档

后端启动后，访问 **`http://localhost:8004/docs`** 查看 Swagger API 文档。

### 主要 API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/pets` | 获取精灵列表（支持筛选、排序） |
| `GET` | `/api/pets/{id}` | 获取单个精灵详情 |
| `POST` | `/api/pets` | 新增精灵 |
| `PUT` | `/api/pets/{id}` | 更新精灵信息 |
| `DELETE` | `/api/pets/{id}` | 删除精灵 |
| `PATCH` | `/api/pets/{id}/toggle-active` | 单个精灵上下架 |
| `PATCH` | `/api/pets/batch-activate` | 一键上架所有精灵 |
| `PATCH` | `/api/pets/batch-deactivate` | 一键下架所有精灵 |
| `GET` | `/api/groups` | 获取所有分组 |
| `GET` | `/api/group-colors` | 获取分组颜色配置 |
| `PUT` | `/api/group-colors/{group}` | 更新分组颜色 |
| `GET` | `/api/announcement` | 获取公告内容 |
| `PUT` | `/api/announcement` | 更新公告内容 |
| `GET` | `/api/messages` | 获取留言列表 |
| `POST` | `/api/messages` | 创建留言 |
| `PUT` | `/api/messages/{id}/read` | 标记留言已读 |
| `DELETE` | `/api/messages/{id}` | 删除留言 |
| `POST` | `/api/admin/login` | 管理员登录 |
| `GET` | `/api/admin/accounts` | 获取管理员列表 |
| `POST` | `/api/admin/accounts` | 创建管理员账号 |

---

## 🎨 开发说明

### 前端代理配置
在 `vite.config.ts` 中配置了以下代理：
- `/api` → `http://localhost:8004`
- `/images` → `http://localhost:8004`
- `/icons` → `http://localhost:8004`

### 后端自动迁移
`main.py` 启动时会自动执行 `auto_migrate()` 函数，检测并创建缺失的表和列，无需手动执行迁移脚本。

### 默认数据初始化
首次启动后端时，会自动创建默认管理员账号（admin / admin123）和初始公告内容。

---

## 🎨 后台主题背景

各管理页面配有独立的洛克王国主题背景图：

| 管理页面 | 背景主题 |
|---|---|
| 精灵管理 | 阿布星星蓝色 |
| 草稿箱 | 菊花梨五角星黄色 |
| 留言管理 | 抹茶布丁绿色爱心 |
| 公告管理 | 独角兽音符粉色 |
| 账号管理 | 小狮鹫蓝色云朵 |

---

## 📦 构建部署

### 前端生产构建

```bash
cd frontend
npm run build
```

构建产物位于 `frontend/dist/` 目录。

### 部署建议
- **前端**：部署到 Vercel（推荐）、Netlify 或静态托管服务
- **后端**：部署到 Railway（推荐）、Heroku 或 AWS
- **数据库**：使用 Railway PostgreSQL 或 SQLite（本地开发）

---

## 📄 License

MIT License

---

## 📮 作者

pipibigking

---

*最后更新：2026-05-15*
