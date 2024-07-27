"""
Function: 事务管理器
Description: 数据库事务管理
    
with TransactionManager(session) 确保在代码块执行完成后，
无论是否发生异常，都会提交或回滚事务，并关闭会话。
    
用法：
# 插入数据
session = Session()
with TransactionManager(session) as tm:
    user1 = User(name='Alice', age=30)
    user2 = User(name='Bob', age=25)
    tm.add(user1)
    tm.add(user2)
    
# 查询数据
session = Session()
with TransactionManager(session) as tm:
    users = tm.query(User).all()
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}, Age: {user.age}")
    
# 更新数据
session = Session()
with TransactionManager(session) as tm:
    user = tm.query(User).filter_by(name='Alice').first()
    if user:
        user.age = 31
        tm.add(user)
    
    # 删除数据
session = Session()
with TransactionManager(session) as tm:
    user = tm.query(User).filter_by(name='Bob').first()
    if user:
        tm.delete(user)
    
    # 批量操作
session = Session()
with TransactionManager(session) as tm:
    # 批量添加
    users = [User(name='Charlie', age=35), User(name='David', age=40)]
    tm.add_all(users)
        
    # 批量更新
    users_to_update = tm.query(User).filter(User.age < 30).all()
    tm.bulk_update(users_to_update, {"age": 30})
        
    # 批量删除
    users_to_delete = tm.query(User).filter(User.age > 50).all()
    tm.bulk_delete(users_to_delete)
"""
class TransactionManager:
    def __init__(self, session):
        self.session = session
        self.affected_rows = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.session.commit()
        else:
            self.session.rollback()
        self.session.close()
        return self.affected_rows

    def add(self, instance):
        """
        向会话中添加单个实例
        :param instance: 要添加的实例
        :return: 添加的行数 (1)
        """
        self.session.add(instance)
        self.affected_rows = 1
        return self.affected_rows

    def add_all(self, instances):
        """
        向会话中添加多个实例
        :param instances: 要添加的实例列表
        :return: 添加的行数
        """
        self.session.add_all(instances)
        self.affected_rows = len(instances)
        return self.affected_rows

    def query(self, *entities):
        """
        创建查询
        :param entities: 要查询的实体
        :return: 查询对象
        """
        return self.session.query(*entities)

    def delete(self, instance):
        """
        从会话中删除单个实例
        :param instance: 要删除的实例
        :return: 删除的行数 (1)
        """
        self.session.delete(instance)
        self.affected_rows = 1
        return self.affected_rows

    def update(self, instance, values):
        """
        更新单个实例
        :param instance: 要更新的实例
        :param values: 包含更新值的字典
        :return: 更新的行数 (1)
        """
        for key, value in values.items():
            setattr(instance, key, value)
        self.affected_rows = 1
        return self.affected_rows

    def bulk_update(self, model, values, condition=None):
        """
        批量更新多个实例
        :param model: 要更新的模型类
        :param values: 包含更新值的字典
        :param condition: 更新条件 (可选)
        :return: 更新的行数
        """
        query = self.session.query(model)
        if condition is not None:
            query = query.filter(condition)
        self.affected_rows = query.update(values, synchronize_session='fetch')
        return self.affected_rows

    def bulk_delete(self, model, condition=None):
        """
        批量删除多个实例
        :param model: 要删除的模型类
        :param condition: 删除条件 (可选)
        :return: 删除的行数
        """
        query = self.session.query(model)
        if condition is not None:
            query = query.filter(condition)
        self.affected_rows = query.delete(synchronize_session='fetch')
        return self.affected_rows