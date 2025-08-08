# Render 部署指南 - Melbourne Parking Website

## 🚀 部署步骤

### 1. 准备 GitHub 仓库
```bash
# 初始化 Git 仓库（如果还没有）
git init
git add .
git commit -m "Initial commit for Render deployment"

# 推送到 GitHub
git remote add origin https://github.com/yourusername/melbourne-parking-website.git
git branch -M main
git push -u origin main
```

### 2. 在 Render 上部署

#### 创建 PostgreSQL 数据库
1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击 "New" → "PostgreSQL"
3. 设置：
   - **Name**: `melbourne-parking-db`
   - **Database**: `melbourne_parking`
   - **User**: `melbourne_user`
   - **Region**: 选择最近的区域
   - **Plan**: Free (免费)
4. 点击 "Create Database"
5. 等待数据库创建完成，记下 **Internal Database URL**

#### 创建 Web Service
1. 在 Render Dashboard 点击 "New" → "Web Service"
2. 连接您的 GitHub 仓库
3. 设置配置：
   - **Name**: `melbourne-parking-api`
   - **Region**: 与数据库相同区域
   - **Branch**: `main`
   - **Root Directory**: 留空
   - **Runtime**: `Python 3`
   - **Build Command**: `chmod +x build.sh && ./build.sh`
   - **Start Command**: `gunicorn app:app`

#### 配置环境变量
在 Web Service 的 "Environment" 选项卡中添加：
```
DATABASE_URL=<你的PostgreSQL Internal Database URL>
SECRET_KEY=<自动生成的密钥>
FLASK_ENV=production
PYTHONPATH=/opt/render/project/src:/opt/render/project/src/backend
```

### 3. 部署前端（可选 - 静态托管）

#### 方法 1: Render Static Site
1. 点击 "New" → "Static Site"
2. 连接同一个 GitHub 仓库
3. 设置：
   - **Name**: `melbourne-parking-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

#### 方法 2: 通过后端服务前端（推荐）
后端已配置为同时服务前端文件，无需额外配置。

### 4. 数据库初始化

部署完成后，需要初始化数据库：

1. 在 Render Web Service 的 "Shell" 选项卡中运行：
```bash
python -c "
import sys
sys.path.insert(0, 'backend')
from website import create_website
from models.parking import db

app = create_website()
with app.app_context():
    db.create_all()
    print('数据库表创建成功')
"
```

2. 如果有初始数据需要导入：
```bash
cd backend/database/seeds
python import_csv_data.py
```

## 🔧 故障排除

### 常见问题

1. **模块导入错误**
   - 确保 `PYTHONPATH` 环境变量包含正确路径
   - 检查 `app.py` 中的路径配置

2. **数据库连接失败**
   - 验证 `DATABASE_URL` 环境变量
   - 确保使用 `postgresql://` 而不是 `postgres://`

3. **构建失败**
   - 检查 `requirements.txt` 中的依赖版本
   - 确保 `build.sh` 有执行权限

### 查看日志
- Web Service: Dashboard → 你的服务 → "Logs" 选项卡
- Database: Dashboard → 你的数据库 → "Logs" 选项卡

## 🌐 访问应用

部署成功后：
- **API 端点**: `https://your-service-name.onrender.com`
- **前端**: `https://your-service-name.onrender.com` (如果通过后端服务)
- **API 文档**: `https://your-service-name.onrender.com/api/`

## 💰 免费额度说明

Render 免费计划包括：
- **Web Services**: 750小时/月 (约31天)
- **PostgreSQL**: 1GB 存储空间，90天数据保留
- **带宽**: 100GB/月
- **自动休眠**: 15分钟无活动后休眠（首次请求需要30秒启动）

## 🔄 后续更新

每次推送到 GitHub main 分支时，Render 会自动重新部署：

```bash
git add .
git commit -m "更新功能"
git push origin main
```

## 📝 注意事项

1. **冷启动**: 免费服务会在无活动时休眠，首次访问可能需要30秒
2. **数据库**: 免费数据库90天后会被删除，建议定期备份
3. **SSL**: Render 自动提供 HTTPS 证书
4. **自定义域名**: 免费计划不支持自定义域名

完成这些步骤后，您的 Melbourne Parking Website 就会在 Render 上运行了！
