# pythonProjectTemplate

## 概要

提供给其他python应用一个统一的框架，包含环境配置、数据库连接、日志、模块集成

## 配置文件

结构：

```bash
pythonProjectTemplate
├── config
│   ├── __init__.py
│   ├── config.py
│   ├── dev.yaml
│   ├── prod.yaml
│   └── test.yaml
├── env.yaml
```

在项目根目录下的env.yaml文件中定义启用的配置文件，env的属性要和config路径下的配置文件名对应，配置哪个就读取哪个yaml文件

```yaml
env:
# 这里env配置为哪个就会对应读取config文件夹下的哪个配置文件
  dev # 开发环境
  #test #测试环境
  #prod #生产环境
```

添加配置时要在config.py中同步修改获取改配置的方法

## Python虚拟环境

1. 在vscode中按下`command+shfit+p`选择python解释器
2. 创建python虚拟环境，选择venv
3. 再次按下`command+shfit+p`选择虚拟环境中的python解释器
4. 重新打开一个终端，这时候应该能看到虚拟环境已经启动
5. 如果还是没有启动，在终端中输入`source .venv/bin/activate`

> 此模板创建时的python版本为`Python 3.9.6`

## 数据库使用

1. MySQL的工具类，内置驱动，见`db/mysql.py`
2. 事务控制见`db/transaction/transaction_manager`

## 动态加载模块

在根目录下的env.yaml文件内module_config.modules下定义需要加载的模块，这样当main.py运行的时候，就会自动执行模块内main.py的run方法

## 依赖

```bash
pip install pyyaml
pip install sqlalchemy
pip install pyyaml python-dotenv
pip install mysql-connector-python
pip install pytest
pip install pymysql
```

## 运行测试

本项目支持运行不同类型的测试。使用以下命令来运行测试：

* 运行所有测试：

  ```
  python tests/run_tests.py all
  ```
* 只运行框架测试：

  ```
  python tests/run_tests.py framework
  ```
* 只运行业务测试：

  ```
  python tests/run_tests.py business
  ```

请确保在运行测试之前已经设置好了正确的环境和依赖。