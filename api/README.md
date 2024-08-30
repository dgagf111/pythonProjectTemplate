# FastAPI Center 使用手册

## 简介

FastAPI Center 是一个基于 FastAPI 框架的 API 服务中心，提供了简单易用的接口管理和后台运行功能。它集成了日志系统、缓存管理等功能，适用于快速构建和部署 RESTful API 服务。

## 特性

1. 异步支持：基于 FastAPI，支持异步请求处理
2. 后台运行：API 服务器在后台线程中运行，不阻塞主程序
3. 日志集成：使用全局日志系统，方便调试和监控
4. 缓存支持：集成缓存管理，提高响应速度
5. 自动文档：利用 FastAPI 的特性，自动生成 API 文档

## 安装

确保您的环境中已安装 Python 3.7+，然后安装所需依赖：

```
pip install fastapi uvicorn pydantic
```

## 使用方法

### 1. 初始化

在您的主程序中，导入并初始化 FastAPICenter：

```python
from api.fastapi_center import FastAPICenter

fastapi_center = FastAPICenter()
```

### 2. 添加路由

在 FastAPICenter 类的 `setup_routes` 方法中添加您的路由：

```14:19:api/fastapi_center.py
class FastAPICenter:
    def __init__(self):
        self.app = FastAPI()
        self.server = None
        self.thread = None
        self.initialize()
```

### 3. 启动服务器

在您的主程序中调用 `start` 方法来启动 API 服务器：

```python
fastapi_center.start()
```

### 4. 关闭服务器

在程序结束时，调用 `shutdown` 方法来优雅地关闭服务器：

```python
fastapi_center.shutdown()
```

## API 示例

以下是一些基本的 API 示例：

1. 健康检查接口

```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

2. 用户操作接口

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # 实现获取用户逻辑
    pass

@app.post("/users/")
async def create_user(user: User):
    # 实现创建用户逻辑
    pass
```

## 测试

使用 pytest 进行测试。在 `tests/framework/api/` 目录下编写测试用例，然后运行：

```
python tests/run_tests.py framework --module api
```

## 配置

API 服务器的配置（如主机、端口等）可以在 `FastAPICenter` 类的 `_run_server` 方法中修改：

```27:29:api/fastapi_center.py
    def _run_server(self):
        self.server = uvicorn.Server(uvicorn.Config(self.app, host="0.0.0.0", port=8000, loop="asyncio"))
        self.server.run()
```

## 最佳实践

1. 使用 Pydantic 模型来验证请求和响应数据
2. 利用 FastAPI 的依赖注入系统来管理共享资源
3. 对于大型应用，将路由分组并使用 APIRouter
4. 使用异步函数来处理 I/O 密集型操作
5. 定期检查和更新依赖包

## 故障排除

* 如果服务器无法启动，检查端口是否被占用
* 确保所有依赖都已正确安装
* 查看日志文件以获取详细的错误信息

## 注意事项

* 在生产环境中，建议使用反向代理（如 Nginx）来管理 FastAPI 应用
* 定期备份数据和配置文件
* 遵循 API 设计最佳实践，如使用适当的 HTTP 方法和状态码

通过遵循本手册，您应该能够轻松地使用 FastAPI Center 来构建和管理您的 API 服务。如有任何问题，请参考 FastAPI 官方文档或联系开发团队。