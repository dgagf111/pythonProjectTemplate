# pythonProjectTemplate

## 概要

这个项目提供了一个统一的Python应用程序框架,包含环境配置、数据库连接、日志记录、API服务、缓存系统、任务调度、消息队列和监控等功能。它旨在为开发者提供一个全面、灵活且易于扩展的项目模板。

## 主要特性

1. 配置管理: 使用YAML文件进行灵活的多环境配置管理
2. 数据库支持: 集成MySQL数据库连接和事务管理
3. 日志系统: 全局日志系统,支持文件和控制台输出
4. API服务: 基于FastAPI的高性能异步API服务
5. 缓存系统: 支持内存缓存和Redis缓存
6. 任务调度: 基于APScheduler的灵活任务调度系统
7. 消息队列: 基于Redis的高性能消息发布和订阅系统
8. 监控系统: 集成Prometheus监控,支持自定义指标和报警
9. 测试框架: 完整的单元测试和集成测试支持
10. 模块化设计: 支持动态加载模块,便于扩展

## 项目结构

```
pythonProjectTemplate
├── api/                 # API服务相关代码
├── cache/               # 缓存系统
├── config/              # 配置文件和配置管理
├── db/                  # 数据库相关代码
├── log/                 # 日志系统
├── monitoring/          # 监控系统
├── redis_msg_center/    # Redis消息队列
├── scheduler/           # 任务调度器
├── tests/               # 测试代码
├── env.yaml             # 环境配置文件
└── main.py              # 主程序入口
```

## 配置文件

### 结构

```
pythonProjectTemplate
├── config
│   ├── __init__.py
│   ├── config.py
│   ├── dev.yaml
│   ├── prod.yaml
│   └── test.yaml
├── env.yaml
```

在项目根目录下的`env.yaml`文件中定义启用的配置文件。`env`属性要和`config`目录下的配置文件名对应,配置哪个就读取哪个yaml文件。

```yaml
env:
# 这里env配置为哪个就会对应读取config文件夹下的哪个配置文件
  dev # 开发环境
  #test #测试环境
  #prod #生产环境
```

添加新配置时,需要在`config.py`中同步修改获取该配置的方法。

## Python虚拟环境

1. 在VSCode中按下`Command+Shift+P`选择Python解释器
2. 创建Python虚拟环境,选择venv
3. 再次按下`Command+Shift+P`选择虚拟环境中的Python解释器
4. 重新打开一个终端,此时应该能看到虚拟环境已经启动
5. 如果还是没有启动,在终端中输入`source .venv/bin/activate`

> 此模板创建时的Python版本为`Python 3.9.6`

## 数据库使用

1. MySQL的工具类,内置驱动,见`db/mysql.py`
2. 事务控制见`db/transaction/transaction_manager`

详细的数据库使用说明请参考 `db/mysql/README.md`。

## API服务

API服务基于FastAPI框架,提供了高性能的异步API支持。主要特性包括:

1. 异步支持:基于 FastAPI,支持异步请求处理
2. 后台运行:API 服务器在后台线程中运行,不阻塞主程序
3. 日志集成:使用全局日志系统,方便调试和监控
4. 缓存支持:集成缓存管理,提高响应速度
5. 自动文档:利用 FastAPI 的特性,自动生成 API 文档
6. 路由管理:支持模块化路由管理
7. 中间件支持:集成自定义中间件,如请求处理时间统计
8. CORS 支持:内置跨域资源共享(CORS)配置

详细使用说明请参考 `api/README.md`。

## 缓存系统

项目提供了一个灵活的缓存系统,支持内存缓存和Redis缓存。主要功能包括:

1. 支持内存缓存和Redis缓存
2. 基本的缓存操作:设置、获取、删除、清空
3. 特殊数据类型操作:列表和哈希
4. 内存缓存支持元组存储

详细说明请参考 `cache/README.md`。

## 任务调度器

项目包含一个基于APScheduler的任务调度系统。主要特性包括:

1. 支持定时任务和间隔任务
2. 自动重试机制
3. 灵活的配置选项
4. 集成全局日志系统

详细使用说明请参考 `scheduler/README.md`。

## 消息队列

项目提供了基于Redis的高性能消息队列系统。主要特性包括:

1. 多主题支持
2. 高并发处理
3. 消息持久化
4. 消息过期机制
5. 错误恢复
6. 异步处理
7. 自定义消费者

详细说明请参考 `redis_msg_center/README.md`。

## 监控系统

监控系统基于Prometheus,提供了指标收集和报警功能。主要组件包括:

1. Prometheus导出器
2. 报警系统
3. 主运行模块

详细说明请参考 `monitoring/README.md`。

## 依赖安装

```bash
pip install pyyaml
pip install sqlalchemy
pip install pyyaml python-dotenv
pip install mysql-connector-python
pip install pytest
pip install pymysql
pip install apscheduler
pip install cachetools redis
pip install prometheus_client psutil
pip install requests
pip install alembic
pip install fastapi uvicorn
pip install httpx
```

## 运行测试

本项目支持运行不同类型的测试。使用以下命令来运行测试:

* 运行所有测试:

  ```
  python tests/run_tests.py all
  ```
* 只运行框架测试:

  ```
  python tests/run_tests.py framework
  ```
* 只运行业务测试:

  ```
  python tests/run_tests.py business
  ```

请确保在运行测试之前已经设置好了正确的环境和依赖。

## 日志系统

本项目使用了一个全局的日志系统。详细的使用说明请参考 `log/README.md`。

## 最佳实践

* 遵循PEP 8编码规范
* 使用虚拟环境管理项目依赖
* 定期运行测试套件确保代码质量
* 使用版本控制系统(如Git)管理代码
* 及时更新文档,特别是在添加新功能或修改现有功能时
* 使用环境变量存储敏感信息,而不是直接在配置文件中硬编码
* 定期审查和更新依赖包
* 对于大型应用,考虑使用微服务架构
* 实施持续集成和持续部署(CI/CD)流程
* 定期进行代码审查,提高代码质量和知识共享

通过使用这个项目模板,您可以快速搭建一个功能齐全、结构清晰的Python应用程序框架,从而提高开发效率和代码质量。如有任何问题或建议,请随时联系项目维护者。