# FastAPI Center 使用手册

## 简介

FastAPI Center 是一个基于 FastAPI 框架的 API 服务中心,提供了简单易用的接口管理和后台运行功能。它集成了日志系统、缓存管理等功能,适用于快速构建和部署 RESTful API 服务。

## 特性

1. 异步支持:基于 FastAPI,支持异步请求处理
2. 后台运行:API 服务器在后台线程中运行,不阻塞主程序
3. 日志集成:使用全局日志系统,方便调试和监控
4. 缓存支持:集成缓存管理,提高响应速度
5. 自动文档:利用 FastAPI 的特性,自动生成 API 文档
6. 路由管理:支持模块化路由管理
7. 中间件支持:集成自定义中间件,如请求处理时间统计
8. CORS 支持:内置跨域资源共享(CORS)配置

## 安装

确保您的环境中已安装 Python 3.7+,然后安装所需依赖:

```
pip install fastapi uvicorn pydantic
```

## 使用方法

### 1. 初始化

在您的主程序中,导入并初始化 FastAPICenter:

```python
from api.fastapi_center import FastAPICenter

fastapi_center = FastAPICenter()
```

### 2. 添加路由

FastAPICenter 支持模块化路由管理。您可以在 `api/routes/` 目录下创建路由模块,然后在 FastAPICenter 类的 `setup_routes` 方法中添加这些路由:

```14:19:api/fastapi_center.py
    id: int
    name: str
    email: str
class FastAPICenter:
    def __init__(self):
```

### 3. 启动服务器

在您的主程序中调用 `start` 方法来启动 API 服务器:

```python
fastapi_center.start()
```

### 4. 关闭服务器

在程序结束时,调用 `shutdown` 方法来优雅地关闭服务器:

```python
fastapi_center.shutdown()
```

## API 示例

以下是一些基本的 API 示例:

1. 健康检查接口

```10:12:api/main.py
@app.get("/")
async def root():
    return {"message": "Hello World"}
```

2. 用户操作接口

```11:21:api/routes/users.py
@router.get("/{user_id}")
async def get_user(user_id: int):
    # 这里应该是从数据库获取用户的逻辑
    if user_id == 1:
        return User(id=1, name="John Doe", email="john@example.com")
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/")
async def create_user(user: User):
    # 这里应该是创建用户的逻辑
    return {"message": "User created successfully", "user_id": user.id}
```

## 配置

API 服务器的配置(如主机、端口等)可以在 `config/dev.yaml` 文件中修改:

```63:96:config/dev.yaml
# API服务器配置
api:
  # 服务器监听的IP地址
  # "0.0.0.0" 表示监听所有可用的网络接口
  host: "0.0.0.0"
  
  # 服务器监听的端口号
  # 8000 是常用的开发端口,生产环境可能需要使用其他端口
  port: 8000
  
  # 事件循环类型
  # "asyncio" 是Python的标准异步IO库,适用于大多数情况
  # 其他选项可能包括 "uvloop" (更快的事件循环实现)
  loop: "asyncio"
  
  # 是否在启动时打开API文档
  # true 表示启动服务器时自动打开Swagger UI文档
  open_api_on_startup: false
  
  # API文档的URL路径
  # "/docs" 是FastAPI的默认Swagger UI路径
  docs_url: "/docs"
  
  # 允许跨域请求的源
  # "*" 表示允许所有源,生产环境应该指定具体的域名
  cors_origins: ["*"]
  
  # 最大并发请求数
  # 控制服务器同时处理的最大请求数,有助于防止过载
  max_concurrency: 100
  
  # 请求超时时间(秒)
  # 如果请求处理时间超过此值,将返回超时错误
  request_timeout: 30
```

## 中间件

FastAPICenter 支持添加自定义中间件。例如,添加处理时间统计中间件:

```109:112:api/fastapi_center.py
    def setup_middleware(self):
        from api.middleware import add_process_time_header
        self.a
```

## CORS 配置

跨域资源共享(CORS)配置也在 `config/dev.yaml` 文件中:

```86:88:config/dev.yaml
  # 允许跨域请求的源
  # "*" 表示允许所有源,生产环境应该指定具体的域名
  cors_origins: ["*"]
```

## 测试

使用 pytest 进行测试。在 `tests/framework/api/` 目录下编写测试用例,然后运行:

```
python tests/run_tests.py framework --module api
```

## 最佳实践

1. 使用 Pydantic 模型来验证请求和响应数据
2. 利用 FastAPI 的依赖注入系统来管理共享资源
3. 对于大型应用,将路由分组并使用 APIRouter
4. 使用异步函数来处理 I/O 密集型操作
5. 定期检查和更新依赖包
6. 利用 FastAPI 的自动文档功能,保持 API 文档的最新状态

## 故障排除

* 如果服务器无法启动,检查端口是否被占用
* 确保所有依赖都已正确安装
* 查看日志文件以获取详细的错误信息

## 注意事项

* 在生产环境中,建议使用反向代理(如 Nginx)来管理 FastAPI 应用
* 定期备份数据和配置文件
* 遵循 API 设计最佳实践,如使用适当的 HTTP 方法和状态码
* 注意处理和记录异常,以便于调试和维护

通过遵循本手册,您应该能够轻松地使用 FastAPI Center 来构建和管理您的 API 服务。如有任何问题,请参考 FastAPI 官方文档或联系开发团队。