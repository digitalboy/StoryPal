# app.py
from app import create_app
from app.config import Config
import logging

# 创建 Flask 应用实例
app = create_app()


if __name__ == "__main__":
    # 启动 Flask 应用
    app.run(debug=Config.DEBUG)
