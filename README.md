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
2. 创建python虚拟环境
3. 再次按下`command+shfit+p`选择虚拟环境中的python解释器

> 此模板创建时的python版本为`Python 3.9.6`

## 数据库使用

1. MySQL的工具类，内置驱动，见`db/mysql_config`
2. 事务控制见`db/transaction`

## 依赖

1. yaml

    ```bash
    pip install pyyaml
    ```

    安装完成后，在Python代码中通过 `import yaml` 来使用YAML功能。
2. sqlalchemy

    ```bash
    pip install sqlalchemy
    ```

    安装完成后，在Python代码中通过 `import sqlalchemy` 来使用sqlalchemy功能。