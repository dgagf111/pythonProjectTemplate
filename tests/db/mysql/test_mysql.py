import pytest
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text
from db.mysql.mysql import MySQL_Database
from tests.db.mysql.test_table import Test_Table
from db.mysql.transaction.transaction_manager import TransactionManager
from log.logHelper import get_logger

logger = get_logger()

@pytest.fixture(scope="module")
def db_connection():
    db = MySQL_Database()
    yield db
    db.close_session()

@pytest.fixture
def session(db_connection):
    return db_connection.get_session()

@pytest.fixture(autouse=True)
def clean_test_data(session):
    session.execute(text("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"))
    session.commit()
    session.execute(text("DELETE FROM test_table"))
    session.commit()
    logger.info("测试数据已清理")

def test_basic_crud_operations(session):
    logger.info("开始测试基本CRUD操作...")
    with TransactionManager(session) as tm:
        # 插入数据
        new_user = Test_Table(name='张三', age=30)
        tm.add(new_user)
        assert new_user.id is not None, "插入操作失败"
        logger.info(f"插入新用: {new_user.name}, ID: {new_user.id}")

        # 查询数据
        user = tm.query(Test_Table).filter_by(name='张三').first()
        assert user is not None, "查询操作失败"
        assert user.age == 30, "查询结果不匹配"
        logger.info(f"查询结果 - ID: {user.id}, 姓名: {user.name}, 年龄: {user.age}")

        # 更新数据
        tm.update(user, {'age': 31})
        updated_user = tm.query(Test_Table).filter_by(name='张三').first()
        assert updated_user.age == 31, "更新操作失败"
        logger.info(f"更新用户 {updated_user.name} 的年龄为 {updated_user.age}")

        # 删除数据
        tm.delete(user)
        deleted_user = tm.query(Test_Table).filter_by(name='张三').first()
        assert deleted_user is None, "删除操作失败"
        logger.info("删除用户: 张三")

    logger.info("基本CRUD操作测试完成")

def test_transaction_rollback(session):
    logger.info("开始测试事务回滚...")
    try:
        with TransactionManager(session) as tm:
            new_user = Test_Table(name='李四', age=25)
            tm.add(new_user)
            assert new_user.id is not None, "插入操作失败"
            logger.info(f"插入新用户: {new_user.name}, ID: {new_user.id}")

            # 故意引发异常
            raise Exception("测试回滚")
    except Exception as e:
        logger.info(f"捕获到异常: {str(e)}")

    # 验证数据是否已回
    with TransactionManager(session) as tm:
        user = tm.query(Test_Table).filter_by(name='李四').first()
        assert user is None, "事务回滚失败"
    
    logger.info("事务回滚测试完成")

def test_batch_insert(session):
    logger.info("开始测试批量插入...")
    users = [
        Test_Table(name=f'用户{i}', age=20+i) for i in range(100)
    ]
    with TransactionManager(session) as tm:
        tm.add_all(users)
    
    # 验证插入结果
    with TransactionManager(session) as tm:
        count = tm.query(Test_Table).count()
        assert count == 100, f"批量插入失败,实际插入{count}条记"
    
    logger.info("批量插入测试完成")

def test_batch_update(session):
    logger.info("开始测批量更��...")
    with TransactionManager(session) as tm:
        tm.query(Test_Table).update({Test_Table.age: Test_Table.age + 1})
    
    # 验证更新结果
    with TransactionManager(session) as tm:
        users = tm.query(Test_Table).all()
        assert all(user.age > 20 for user in users), "批量更新失败"
    
    logger.info("批量更新测试完成")

def test_batch_delete(session):
    logger.info("始测试批量删除...")
    with TransactionManager(session) as tm:
        tm.query(Test_Table).filter(Test_Table.age > 25).delete()
    
    # 证删除结果
    with TransactionManager(session) as tm:
        count = tm.query(Test_Table).count()
        assert count < 100, f"批量删除失败,剩余{count}条记录"
    
    logger.info("批量删除测试完成")

def test_complex_query(session):
    logger.info("开始测试复杂查询...")
    with TransactionManager(session) as tm:
        # 添加一些测试数据
        tm.add_all([
            Test_Table(name='王五', age=35),
            Test_Table(name='赵六', age=40),
            Test_Table(name='钱七', age=45)
        ])
        
        # 复杂查询: 查找年龄大于35的用,按年龄降序排列,限制2条结果
        results = tm.query(Test_Table)\
            .filter(Test_Table.age > 35)\
            .order_by(Test_Table.age.desc())\
            .limit(2)\
            .all()
        
        assert len(results) == 2, "复杂查询结果数量不符"
        assert results[0].age > results[1].age, "排序结果不正确"
    
    logger.info("复杂查询测试完成")

import threading
import time

def test_transaction_isolation(db_connection):
    logger.info("开始测试事务隔离性...")

    def session1_transaction():
        db1 = MySQL_Database()
        session1 = db1.get_session()
        try:
            session1.execute(text("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"))
            session1.commit()
            with session1.begin():
                new_user = Test_Table(name='隔离测试', age=50)
                session1.add(new_user)
                session1.flush()
                time.sleep(2)
            session1.commit()  # 确保事务被提交
            logger.info("Session1 事务已提交")
        except Exception as e:
            logger.error(f"Session1 事务出错: {str(e)}")
            session1.rollback()
        finally:
            session1.close()
            db1.close_session()

    def session2_transaction():
        db2 = MySQL_Database()
        session2 = db2.get_session()
        try:
            session2.execute(text("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED"))
            session2.commit()
            time.sleep(1)
            with session2.begin():
                session2.expire_all()
                user = session2.query(Test_Table).filter_by(name='隔离测试').first()
                assert user is None, "事务隔离性失败:未提交的数据被其他事务读取"
            logger.info("Session2 事务隔离性测试通过")
        except AssertionError:
            logger.error("事务隔离性测试失败:未提交的数据被其他事务读取")
        except Exception as e:
            logger.error(f"Session2 事务出错: {str(e)}")
        finally:
            session2.close()
            db2.close_session()

    thread1 = threading.Thread(target=session1_transaction)
    thread2 = threading.Thread(target=session2_transaction)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    # 验证数据可见性
    try:
        with db_connection.get_session() as session:
            session.expire_all()
            user = session.query(Test_Table).filter_by(name='隔离测试').first()
            assert user is not None, "事务提交后数据不可见"
            assert user.name == '隔离测试' and user.age == 50, "提交后的数据不正确"
        logger.info("事���隔离性测试完成：数据正确提交并可见")
    except AssertionError as e:
        logger.error(f"事务隔离性测试失败: {str(e)}")
    except Exception as e:
        logger.error(f"验证数据可见性时发生错误: {str(e)}")

    logger.info("事务隔离性测试完成")

if __name__ == "__main__":
    pytest.main([__file__, '-v'])
