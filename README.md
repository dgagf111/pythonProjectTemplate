# pythonProjectTemplate

## 概要

这个项目提供了一个统一的Python应用程序框架,包含环境配置、数据库连接、日志记录、API服务、缓存系统、任务调度和监控等功能。它旨在为开发者提供一个全面、灵活且易于扩展的项目模板。

## 主要特性

1. 配置管理: 使用YAML文件进行灵活的多环境配置管理
2. 数据库支持: 集成MySQL数据库连接和事务管理
3. 日志系统: 全局日志系统,支持文件和控制台输出
4. API服务: 基于FastAPI的高性能异步API服务
5. 缓存系统: 支持内存缓存和Redis缓存
6. 任务调度: 基于APScheduler的灵活任务调度系统
7. 监控系统: 集成Prometheus监控,支持自定义指标和报警
8. 测试框架: 完整的单元测试和集成测试支持
9. 模块化设计: 支持动态加载模块,便于扩展
10. Docker支持: 包含Dockerfile,便于容器化部署

## 项目结构

```
pythonProjectTemplate
├── api/                 # API服务相关代码
├── cache/               # 缓存系统
├── config/              # 配置文件和配置管理
├── db/                  # 数据库相关代码
├── log/                 # 日志系统
├── monitoring/          # 监控系统
├── scheduler/           # 任务调度器
├── tests/               # 测试代码
├── env.yaml             # 环境配置文件
├── main.py              # 主程序入口
├── Dockerfile           # Docker构建文件
├── requirements.txt     # 项目依赖文件
└── update_requirements.py # 更新依赖文件的脚本
```

## 配置文件

配置文件结构:

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

在`env.yaml`文件中定义启用的配置文件。添加新配置时,需要在`config.py`中同步修改获取该配置的方法。

## Python虚拟环境

1. 在VSCode中选择Python解释器
2. 创建Python虚拟环境,选择venv
3. 选择虚拟环境中的Python解释器
4. 重新打开终端,确认虚拟环境已启动
5. 如未启动,输入`source .venv/bin/activate`

## 依赖管理

安装依赖:

```bash
pip install -r requirements.txt
```

更新requirements.txt:

```bash
python update_requirements.py
```

## Docker支持

构建镜像:

```bash
docker build -t pythonprojecttemplate .
```

运行容器:

```bash
docker run -p 8000:8000 pythonprojecttemplate
```

## 模块说明

* 数据库: 详见`db/mysql/README.md`
* API服务: 详见`api/README.md`
* 缓存系统: 详见`cache/README.md`
* 任务调度器: 详见`scheduler/README.md`
* 监控系统: 详见`monitoring/README.md`
* 日志系统: 详见`log/README.md`

## 运行测试

运行所有测试:

```
python tests/run_tests.py all
```

运行框架测试:

```
python tests/run_tests.py framework
```

运行业务测试:

```
python tests/run_tests.py business
```

详细测试说明见`tests/README.md`。

## 最佳实践

* 遵循PEP 8编码规范
* 使用虚拟环境管理依赖
* 定期运行测试套件
* 使用版本控制系统
* 及时更新文档
* 使用环境变量存储敏感信息
* 定期审查和更新依赖包
* 考虑使用微服务架构
* 实施CI/CD流程
* 定期进行代码审查

如有任何问题或建议,请联系项目维护者。