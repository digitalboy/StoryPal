# 1. 使用官方的 Python 3.12 slim 版本作为基础镜像
FROM python:3.12-slim

# 2. 设置环境变量，防止 Python 写入 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE 1
# 3. 设置环境变量，确保 Python 输出是无缓冲的
ENV PYTHONUNBUFFERED 1

# 4. 在容器内创建工作目录
WORKDIR /app

# 5. 复制依赖文件到工作目录
COPY requirements.txt .

# 6. 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 7. 复制项目代码到工作目录
COPY . .

# 8. 暴露 gunicorn 运行的端口
EXPOSE 5000

# 9. 定义容器启动时运行的命令
# 使用 gunicorn 启动应用
# -w 4: 使用 4 个 worker 进程
# -b 0.0.0.0:5000: 绑定到所有网络接口的 5000 端口
# app:app: 运行 app.py 文件中的 app 实例
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]