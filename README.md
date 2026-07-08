# 🎬 电影平台 (Movie Platform)

一个基于 Flask 的电影信息展示与资源管理平台，支持电影搜索、在线播放、收藏和观影历史记录等功能。

---

## ✨ 功能特点

- 🔐 **用户系统**：注册、登录、个人中心
- 🎥 **电影管理**：电影列表、详情页、分类筛选
- 🔍 **搜索功能**：按片名搜索电影
- ▶️ **在线播放**：支持 iframe 嵌入播放
- ⭐ **收藏功能**：收藏喜欢的电影
- 📊 **观影历史**：自动记录观看记录
- 🖼️ **首页轮播**：动态轮播图展示
- 👑 **会员管理**：会员等级和权益

## 🛠️ 技术栈

| 技术 | 用途 |
| :--- | :--- |
| **Flask** | Web 框架 |
| **SQLAlchemy** | ORM 数据库操作 |
| **Flask-Login** | 用户登录管理 |
| **Jinja2** | 前端模板引擎 |
| **MySQL** | 数据库 |
| **requests** | 网络请求 |
| **yt-dlp** | 视频爬虫 |

## 📦 安装与运行

### 1. 克隆项目

```bash
git clone git@github.com:Sakimi-whit/Movie-open.git
cd Movie-open
```

### 2. 创建虚拟环境

```bash
python -m venv .venv312
source .venv312/Scripts/activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python init_data.py
```

### 5. 启动项目

```bash
python app.py
```

访问 http://127.0.0.1:5000 即可查看。
