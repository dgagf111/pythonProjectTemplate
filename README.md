# pythonProjectTemplate

## 概要

这个项目提供了一个统一的Python应用程序框架,包含环境配置、数据库连接、日志记录和模块集成等功能。

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

```1:5:env.yaml
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

## 动态加载模块

在根目录下的`env.yaml`文件内`module_config.modules`下定义需要加载的模块,这样当`main.py`运行时,就会自动执行模块内`main.py`的`run`方法。

## 依赖

```bash
pip install pyyaml
pip install sqlalchemy
pip install pyyaml python-dotenv
pip install mysql-connector-python
pip install pytest
pip install pymysql
pip install apscheduler
pip install cachetools redis
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

## 缓存系统

项目提供了一个灵活的缓存系统,支持内存缓存和Redis缓存。详细说明请参考 `cache/README.md`。

## 定时任务调度器

项目包含一个基于APScheduler的任务调度系统。使用说明请参考 `scheduler/README.md`。

## 配置管理

项目使用YAML文件进行配置管理。详细说明请参考 `config/README.md`。

## 最佳实践

* 遵循PEP 8编码规范
* 使用虚拟环境管理项目依赖
* 定期运行测试套件确保代码质量
* 使用版本控制系统(如Git)管理代码
* 及时更新文档,特别是在添加新功能或修改现有功能时