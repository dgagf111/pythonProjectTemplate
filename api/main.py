from fastapi import FastAPI
from log.logHelper import get_logger
from cache.cache_manager import get_cache_manager

logger = get_logger()
cache = get_cache_manager()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/cache/{key}")
async def get_cache(key: str):
    value = cache.get(key)
    return {"key": key, "value": value}

@app.post("/cache/{key}")
async def set_cache(key: str, value: str):
    cache.set(key, value)
    return {"message": "Cache set successfully"}
