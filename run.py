# run.py
from app import create_app
import os

# 创建 Flask 应用实例
app = create_app()

if __name__ == "__main__":
    # 从环境变量获取主机和端口，如果没有则使用默认值
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))

    # 运行应用
    # debug=True 会在代码更改时自动重启服务器，并且在出错时提供详细的调试信息
    app.run(host=host, port=port, debug=app.debug)
