# MySQL 功能说明

本项目提供了一个强大的MySQL数据库接口，封装了常用的数据库操作和事务管理。主要功能包括：

## 1. 数据库连接

使用`MySQL_Database`类来创建数据库连接。这个类会自动从配置文件中读取数据库配置信息。

使用示例：

```python
from db.mysql.mysql import MySQL_Database
db = MySQL_Database()
```

## 2. 会话管理

`MySQL_Database`类提供了获取和关闭数据库会话的方法。

使用示例：

```python
session = db.get_session()
db.close_session()
```

## 3. 事务管理

使用`TransactionManager`类来管理事务。它提供了一个上下文管理器，确保事务的正确提交或回滚。

使用示例：

```python
from db.mysql.transaction.transaction_manager import TransactionManager
with TransactionManager(session) as tm:
    # 执行数据库操作
    tm.add(new_user)
    tm.update(user, {'age': 31})
```

## 4. CRUD操作

`TransactionManager`类封装了基本的CRUD（创建、读取、更新、删除）操作。

* 添加：`tm.add(object)`
* 查询：`tm.query(Model).filter_by(condition).first()`
* 更新：`tm.update(object, {'field': new_value})`
* 删除：`tm.delete(object)`

## 5. 批量操作

支持批量添加、更新和删除操作，提高大量数据处理的效率。

* 批量添加：`tm.add_all(objects)`
* 批量更新：`tm.query(Model).update({Model.field: new_value})`
* 批量删除：`tm.query(Model).filter(condition).delete()`

## 6. 复杂查询

支持复杂的查询操作，包括过滤、排序、限制结果数量等。

使用示例：
‍`python results = tm.query(Model).filter(Model.age > 30).order_by(Model.age.desc()).limit(10).all() ‍`

## 7. 参数化查询（防SQL注入）

提供`execute_parameterized_query`方法执行参数化查询，有效防止SQL注入攻击。

使用示例：
‍`python query = "SELECT * FROM users WHERE username = :username AND age > :age" params = {"username": user_input, "age": 18} result = tm.execute_parameterized_query(query, params) ‍`

## 8. 事务隔离

支持设置事务隔离级别，默认使用"READ COMMITTED"级别。

## 9. 自动创建表

`MySQL_Database`类在初始化时会自动检查并创建必要的数据库表。

使用这些功能时，请参考相应的测试文件以获取更详细的使用示例：

‍`python:tests/framework/db/mysql/test_mysql.py startLine: 1 endLine: 208 ‍`

这些测试文件展示了各种数据库操作的具体使用方法和最佳实践。<br />