#!/bin/bash

# Render 部署构建脚本
echo "开始 Render 部署构建..."

# 安装 Python 依赖
pip install -r requirements.txt

# 初始化数据库（如果需要）
if [ "$DATABASE_URL" ]; then
    echo "正在初始化数据库..."
    python -c "
import os
import sys
sys.path.insert(0, 'backend')
from website import create_website
from models.parking import db

app = create_website()
with app.app_context():
    try:
        db.create_all()
        print('数据库表创建成功')
    except Exception as e:
        print(f'数据库初始化错误: {e}')
"
fi

echo "构建完成！"
