from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from log.logHelper import get_logger
import threading
from fastapi.middleware.cors import CORSMiddleware
from config.config import config
import time

logger = get_logger()

class User(BaseModel):
    id: int
    name: str
    email: str

class FastAPICenter:
    def __init__(self):
        self.app = FastAPI()
        self.server = None
        self.thread = None
        self.config = config  # 添加这行
        self.should_exit = threading.Event()  # 添加这行
        self.initialize()

    def start(self):
        logger.info("启动FastAPI服务器...")
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        logger.info("FastAPI服务器已在后台启动")

    def _run_server(self):
        api_config = self.config.get_api_config()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=api_config['cors_origins'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        config = uvicorn.Config(
            self.app,
            host=api_config['host'],
            port=api_config['port'],
            loop=api_config['loop'],
            limit_concurrency=api_config['max_concurrency'],
            timeout_keep_alive=api_config['request_timeout']
        )
        self.server = uvicorn.Server(config)
        if api_config['open_api_on_startup']:
            import webbrowser
            webbrowser.open(f"http://{api_config['host']}:{api_config['port']}{api_config['docs_url']}")
        
        # 使用 should_exit 事件来控制服务器运行
        while not self.should_exit.is_set():
            self.server.run(None)  # 非阻塞运行
            time.sleep(1)  # 避免过度占用 CPU

    async def shutdown(self):
        if self.should_exit.is_set():
            return
        logger.info("正在关闭FastAPI服务器...")
        self.should_exit.set()
        if self.server:
            self.server.should_exit = True
            await self.server.shutdown()
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("FastAPI服务器已关闭")

    def initialize(self):
        self.setup_routes()
        self.setup_middleware()

    def setup_routes(self):
        @self.app.get("/")
        async def read_main():
            return {"message": "Hello World"}

        @self.app.get("/hello/{name}")
        async def read_hello(name: str):
            return {"message": f"Hello {name}"}

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}

        @self.app.get("/users/{user_id}")
        async def get_user(user_id: int):
            if user_id == 1:
                return User(id=1, name="John Doe", email="john@example.com")
            raise HTTPException(status_code=404, detail="User not found")

        @self.app.post("/users/")
        async def create_user(user: User):
            return {"message": "User created successfully", "user_id": user.id}

        @self.app.get("/cache/{key}")
        async def get_cache(key: str):
            # 这里应该实现实际的缓存获取逻辑
            return {"key": key, "value": "cached_value"}

        @self.app.post("/cache/{key}")
        async def set_cache(key: str, value: str):
            # 这里应该实现实际的缓存设置逻辑
            return {"message": "Cache set successfully"}

    def setup_middleware(self):
        from api.middleware import add_process_time_header
        self.app.middleware("http")(add_process_time_header)

    # 其他方法保持不变

fastapi_center = FastAPICenter()
