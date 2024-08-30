# 缓存模块说明

本项目提供了一个灵活的缓存系统，支持内存缓存和 Redis 缓存。主要功能包括：

## 1. 缓存类型

* 内存缓存：使用 Python 的内置数据结构实现，支持所有 Python 数据类型，包括元组。
* Redis 缓存：使用 Redis 数据库实现，不支持直接存储元组。

## 2. 缓存管理器

使用 `get_cache_manager` 函数来创建适当的缓存管理器实例：

```python
from cache import get_cache_manager

config = {
    'type': 'memory',  # 或 'redis'
    'ttl': 3600,
    'max_size': 1000,  # 仅用于内存缓存
    'redis': {  # 仅用于 Redis 缓存
        'host': 'localhost',
        'port': 6379,
        'db': 0
    }
}

cache = get_cache_manager(config)
```

## 3. 基本操作

* 设置缓存：`cache.set(key, value, ttl=None)`
* 获取缓存：`cache.get(key)`
* 删除缓存：`cache.delete(key)`
* 清空缓存：`cache.clear()`

## 4. 特殊数据类型操作

* 列表操作：

  * 设置：`cache.set_list(key, value_list, ttl=None)`
  * 获取：`cache.get_list(key)`
* 哈希操作：

  * 设置：`cache.set_hash(key, value_dict, ttl=None)`
  * 获取：`cache.get_hash(key)`

## 5. 元组支持

* 内存缓存：完全支持元组的存储和检索。
* Redis 缓存：不支持元组。尝试存储元组将引发 `ValueError` 异常。

示例：

```python
# 内存缓存
memory_cache.set("tuple_key", (1, 2, 3))  # 正常工作

# Redis 缓存
try:
    redis_cache.set("tuple_key", (1, 2, 3))
except ValueError as e:
    print(f"错误：{e}")  # 输出: 错误：Redis缓存不支持存储元组类型。请使用列表代替。
```

## 6. 最佳实践

* 对于需要跨平台兼容性的代码，避免直接使用元组，而是使用列表代替。
* 在使用 Redis 缓存时，始终将元组转换为列表后再存储。
* 使用 try-except 块来处理可能的 `ValueError`，以确保代码的健壮性。

通过遵循这些指南，您可以有效地使用缓存系统，同时避免与元组相关的兼容性问题。