from mysql_config.mysql import MySQL_Database
from mysql_config.test_table import Test_Table

if __name__ == "__main__":
    # 实例化数据库工具类（自动读取当前路径下的配置文件）
    db = MySQL_Database()

    # 获取会话
    session = db.get_session()

    # 插入数据
    new_user = Test_Table(name='John Doe', age=30)
    session.add(new_user)
    session.commit()

    # 查询数据
    users = session.query(Test_Table).all()
    for user in users:
        print(f'ID: {user.id}, Name: {user.name}, Age: {user.age}')

    # 更新数据
    user_to_update = session.query(Test_Table).filter_by(name='John Doe').first()
    if user_to_update:
        user_to_update.age = 31
        session.commit()

    # 删除数据
    user_to_delete = session.query(Test_Table).filter_by(name='John Doe').first()
    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()

    # 关闭会话
    db.close_session()