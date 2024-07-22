# pythonProjectTemplate

## 概要

提供给其他python应用一个统一的框架，包含环境配置、数据库连接、日志、模块集成

## Python虚拟环境

在vscode中按下`command+shfit+p`选择python解释器，在选择之前创建python虚拟环境，创建后再次选择按下`command+shfit+p`选择虚拟环境中的python解释器，此模板创建时的python版本为`Python 3.9.6`

## 数据库使用

工程内置MySQL的工具类，见db/mysql_config路径，同时支持事务控制，见db/transaction路径

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