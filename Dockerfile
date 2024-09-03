# 使用官方Python 3.12镜像作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 设置环境变量
# python 不缓存输出
ENV PYTHONUNBUFFERED=1
# 设置数据库连接信息
ENV MYSQL_USERNAME=discordbot
ENV MYSQL_PASSWORD=96b0_8GoLl^y7!Vm(T.2fWY?dJe41HQv
ENV MYSQL_HOST=116.198.240.197
ENV MYSQL_PORT=3306
ENV MYSQL_DATABASE=discordbot_test
ENV REDIS_HOST=host.docker.internal
ENV REDIS_PORT=6379
# 设置API版本，优先使用环境变量，如果没有设置则使用配置文件中的值
ENV API_VERSION=v1

# 暴露API服务端口
EXPOSE 8000

# 运行测试，然后启动应用
CMD python tests/run_tests.py framework && python main.py
