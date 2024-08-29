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
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import text
from sqlalchemy import text

class TransactionManager:
    def __init__(self, session):
        self.session = session
        self.affected_rows = 0
        self._transaction = None

    def __enter__(self):
        if not self.session.in_transaction():
            self._transaction = self.session.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            if self._transaction:
                self._transaction.rollback()
        else:
            if self._transaction:
                self._transaction.commit()
        self._transaction = None

    def add(self, instance):
        """向会话中添加单个实例"""
        self.session.add(instance)
        self.session.flush()  # 刷新会话以获取新插入记录的ID
        self.affected_rows = 1
        return self.affected_rows

    def add_all(self, instances):
        """向会话中添加多个实例"""
        self.session.add_all(instances)
        self.session.flush()  # 刷新会话以获取新插入记录的ID
        self.affected_rows = len(instances)
        return self.affected_rows

    def query(self, *entities):
        """创建查询"""
        return self.session.query(*entities)

    def delete(self, instance):
        """从会话中删除个实例"""
        if instance not in self.session:
            raise ValueError("Instance is not in the session")
        self.session.delete(instance)
        self.affected_rows = 1
        return self.affected_rows

    def update(self, instance, values):
        """更新单个实例"""
        if instance not in self.session:
            raise NoResultFound("Instance not found in the database")
        for key, value in values.items():
            setattr(instance, key, value)
        self.affected_rows = 1
        return self.affected_rows

    def bulk_update(self, model, values, condition=None):
        """批量更新多个实例"""
        query = self.session.query(model)
        if condition is not None:
            query = query.filter(condition)
        self.affected_rows = query.update(values, synchronize_session='fetch')
        return self.affected_rows

    def bulk_delete(self, model, condition=None):
        """批量删除多个实例"""
        query = self.session.query(model)
        if condition is not None:
            query = query.filter(condition)
        self.affected_rows = query.delete(synchronize_session='fetch')
        return self.affected_rows

    def get_affected_rows(self):
        """获取受影响的行数"""
        return self.affected_rows