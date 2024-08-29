# 调度器使用指南

## 1. 简介

这个调度器是一个基于 APScheduler 的任务调度系统，提供了灵活的任务配置和执行机制。它支持定时任务、间隔任务，并具有自动重试功能。

## 2. 配置任务

任务配置在 `config/dev.yaml` 文件中进行。每个任务需要以下配置：


```9:44:config/dev.yaml
# 定时器任务配置
tasks:
  # 配置说明：
  # trigger: 定义任务的触发方式
  #   - interval: 间隔触发，可以使用 weeks, days, hours, minutes, seconds 等参数
  #   - cron: 在特定时间触发，使用 cron 表达式格式
  #   - date: 在指定日期时间触发（单次）
  # args: 触发器的具体参数，根据 trigger 类型而不同
  # max_attempts: 任务失败后的最大重试次数
  #   - 如果任务执行失败，调度器会尝试重新执行，直到达到这个次数
  # retry_delay: 重试之间的等待时间（秒）
  #   - 每次重试之前，调度器会等待这里指定的秒数
    args:
  # 任务1配置
  task1:
    # 触发器类型：每隔一定时间执行一次
    trigger: interval
    # 触发器参数：每10秒执行一次
    args:
      seconds: 1
    # 重试机制-最大重试次数：如果任务失败，最多重试3次
    max_attempts: 3
    # 重试机制-重试延迟：每次重试之间等待2秒
    retry_delay: 2
  # 任务2配置
  task2:
    # 触发器类型：在特定时间执行
    trigger: cron
    # 触发器参数：每天12:00执行
    args:
      hour: 12
      minute: 0
    # 重试机制-最大重试次数：如果任务失败，最多重试5次
    max_attempts: 5
    # 重试机制-重试延迟：每次重试之间等待5秒
    retry_delay: 5
```


## 3. 创建任务

1. 在 `scheduler/tasks/` 目录下创建新的 Python 文件，例如 `task1.py`。
2. 在文件中定义一个 `run()` 函数作为任务的入口点：


```1:6:scheduler/tasks/task1.py
from log.logHelper import get_logger

logger = get_logger()

def run():
    logger.info("执行任务1")
```


## 4. 启动调度器

调度器会在应用程序启动时自动启动。在 `main.py` 中：


```86:90:main.py
    logger.info("应用程序启动")
    
    # 启动调度中心
    scheduler_center.start()
    logger.info("调度中心已启动")
```


## 5. 调度器配置

可以在 `env.yaml` 文件中配置调度器的全局设置：


```41:64:env.yaml
scheduler:
  # jobstore:
    # 作业存储的数据库连接URL
    # mysql+pymysql: 使用PyMySQL驱动连接MySQL数据库
    # username: 数据库用户名
    # password: 数据库密码
    # host: 数据库服务器地址
    # port: 数据库服务器端口
    # database: 要使用的数据库名称
    # url: mysql+pymysql://username:password@host:port/database
  executors:
    # 默认线程池的线程数量
    # 用于并发执行较轻量级的任务
    default_threads: 20
    # 进程池的进程数量
    # 用于执行CPU密集型或需要独立Python解释器的任务
    process_pool: 5
  job_defaults:
    # 是否合并执行错过的任务
    # false表示不合并,每个错过的任务都会被单独执行
    coalesce: false
    # 同一个任务的最大同时运行实例数
    # 3表示同一个任务最多可以有3个实例同时运行
    max_instances: 3
```


## 6. 日志

调度器使用全局日志系统。您可以在任务中使用以下方式记录日志：

```python
from log.logHelper import get_logger

logger = get_logger()
logger.info("任务执行信息")
logger.error("任务执行错误")
```

## 7. 重试机制

任务失败时会自动重试。重试次数和延迟可在任务配置中设置：


```29:32:config/dev.yaml
    # 重试机制-最大重试次数：如果任务失败，最多重试3次
    max_attempts: 3
    # 重试机制-重试延迟：每次重试之间等待2秒
    retry_delay: 2
```


## 8. 停止服务

要优雅地停止服务，可以发送 SIGINT 或 SIGTERM 信号，或使用 Ctrl+C：


```95:102:main.py
    try:
        # 使用 signal.pause() 等待信号
        logger.info("主程序进入等待状态，按 Ctrl+C 或发送 SIGTERM 信号来停止服务")
        signal.pause()
    except KeyboardInterrupt:
        logger.info("接收到键盘中断")
    finally:
        graceful_shutdown()
```


## 9. 注意事项

- 确保所有任务模块都位于 `scheduler/tasks/` 目录下。
- 任务名称应与配置文件中的键名匹配。
- 避免在任务中执行长时间阻塞的操作，可能会影响其他任务的调度。

## 10. 故障排除

- 如果任务未执行，检查配置文件和任务模块是否正确。
- 查看日志文件以获取详细的错误信息和任务执行状态。

通过遵循这个指南，用户应该能够轻松地配置和使用这个调度器系统。如有任何问题，请参考源代码或联系开发团队。