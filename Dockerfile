# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV MYSQL_HOST=116.198.240.197
ENV MYSQL_PORT=3306
ENV REDIS_HOST=host.docker.internal
ENV REDIS_PORT=6379
# 设置API版本，优先使用环境变量，如果没有设置则使用配置文件中的值
ENV API_VERSION=v1

# 暴露API服务端口
EXPOSE 8000

# # 运行应用
# CMD ["python", "main.py"]
# 运行测试和应用
CMD ["sh", "-c", "python tests/run_tests.py all && python main.py"]
