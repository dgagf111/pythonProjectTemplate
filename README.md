# pythonProjectTemplate

## 概要

提供给其他python应用一个统一的框架，包含环境配置、数据库连接、日志、模块集成

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