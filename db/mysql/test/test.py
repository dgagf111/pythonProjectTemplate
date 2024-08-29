import sys
import os
import unittest
from sqlalchemy import text
from sqlalchemy.orm.exc import NoResultFound

# 添加项目根目录到Python路径，确保可以导入所需模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from db.mysql.mysql import MySQL_Database
from db.mysql.test.test_table import Test_Table
from db.mysql.transaction.transaction_manager import TransactionManager
from log.logHelper import get_logger

logger = get_logger()

class TestDatabaseOperations(unittest.TestCase):
    """
    数据库操作测试类
    
    本测试类旨在全面测试数据库操作和事务管理功能，包括：
    1. 基本的CRUD（创建、读取、更新、删除）操作
    2. 批量操作（批量插入、更新、删除）
    3. 事务管理（提交和回滚）
    4. 错误处理
    
    特性：
    - 数据清理：每个测试方法执行前都会清理测试数据，确保测试环境的一致性
    - 事务管理：使用TransactionManager确保操作的原子性和一致性
    - 异常处理：测试异常情况，如操作不存在的记录
    - 日志记录：详细记录每个测试步骤，便于调试和监控
    
    运行此文件将执行所有测试用例，全面验证数据库操作的正确性和稳定性。
    """

    @classmethod
    def setUpClass(cls):
        """
        在所有测试开始前执行一次
        初始化数据库连接
        """
        cls.db = MySQL_Database()
        cls.session = cls.db.get_session()
        logger.info("数据库连接初始化完成")

    @classmethod
    def tearDownClass(cls):
        """
        在所有测试结束后执行一次
        关闭数据库连接
        """
        cls.db.close_session()
        logger.info("数据库连接已关闭")

    def setUp(self):
        """
        在每个测试方法开始前执行
        清理测试数据，确保每个测试都在干净的环境中运行
        """
        self.clean_test_data()

    def clean_test_data(self):
        """
        清理测试数据
        删除所有测试用的记录，保证测试环境的一致性
        """
        with TransactionManager(self.session) as tm:
            tm.query(Test_Table).delete()
        logger.info("测试数据已清理")

    def test_basic_crud_operations(self):
        """
        测试基本的CRUD操作
        
        包括：
        1. 插入一条新记录
        2. 查询并验证插入的记录
        3. 更新记录
        4. 删除记录
        
        这个测试确保了最基本的数据库操作都能正确执行。
        """
        logger.info("开始测试基本CRUD操作...")
        with TransactionManager(self.session) as tm:
            # 插入数据
            new_user = Test_Table(name='张三', age=30)
            tm.add(new_user)
            self.assertIsNotNone(new_user.id, "插入操作失败")
            logger.info(f"插入新用户: {new_user.name}, ID: {new_user.id}")

            # 查询数据
            user = tm.query(Test_Table).filter_by(name='张三').first()
            self.assertIsNotNone(user, "查询操作失败")
            self.assertEqual(user.age, 30, "查询结果不匹配")
            logger.info(f"查询结果 - ID: {user.id}, 姓名: {user.name}, 年龄: {user.age}")

            # 更新数据
            tm.update(user, {'age': 31})
            updated_user = tm.query(Test_Table).filter_by(name='张三').first()
            self.assertEqual(updated_user.age, 31, "更新操作失败")
            logger.info(f"更新用户 {updated_user.name} 的年龄为 {updated_user.age}")

            # 删除数据
            tm.delete(user)
            deleted_user = tm.query(Test_Table).filter_by(name='张三').first()
            self.assertIsNone(deleted_user, "删除操作失败")
            logger.info("删除用户: 张三")

        logger.info("基本CRUD操作测试完成")

    def test_bulk_operations(self):
        """
        测试批量操作
        
        包括：
        1. 批量插入多条记录
        2. 批量更新符合条件的记录
        3. 批量删除符合条件的记录
        
        这个测试验证了系统处理大量数据的能力，对于性能优化很重要。
        """
        logger.info("开始测试批量操作...")
        with TransactionManager(self.session) as tm:
            # 批量插入
            users = [Test_Table(name=f'User{i}', age=20+i) for i in range(5)]
            tm.add_all(users)
            self.assertEqual(tm.query(Test_Table).count(), 5, "批量插入失败")
            logger.info("批量插入5条记录成功")

            # 批量更新
            affected_rows = tm.bulk_update(Test_Table, {'age': 30}, Test_Table.age < 23)
            self.assertEqual(affected_rows, 3, "批量更新失败")
            logger.info(f"批量更新成功，影响了 {affected_rows} 条记录")

            # 批量删除
            tm.bulk_delete(Test_Table, Test_Table.age == 30)
            self.assertEqual(tm.query(Test_Table).count(), 2, "批量删除失败")
            logger.info("批量删除成功")

        logger.info("批量操作测试完成")

    def test_transaction_commit(self):
        """
        测试事务提交
        
        在一个事务中执行多个操作，然后提交：
        1. 插入两条记录
        2. 更新一条记录
        3. 删除一条记录
        
        这个测试确保了事务的原子性，所有操作要么全部成功，要么全部失败。
        """
        logger.info("开始测试事务提交...")
        with TransactionManager(self.session) as tm:
            # 在事务中插入两条记录
            user1 = Test_Table(name='Alice', age=25)
            user2 = Test_Table(name='Bob', age=30)
            tm.add(user1)
            tm.add(user2)
            logger.info("事务中插入了两条记录")

            # 在事务中更新一条记录
            tm.update(user1, {'age': 26})
            logger.info("事务中更新了一条记录")

            # 在事务中删除一条记录
            tm.delete(user2)
            logger.info("事务中删除了一条记录")

        # 验证事务结果
        with TransactionManager(self.session) as tm:
            users = tm.query(Test_Table).all()
            self.assertEqual(len(users), 1, "事务提交后记录数量不正确")
            self.assertEqual(users[0].name, 'Alice', "事务提交后记录不匹配")
            self.assertEqual(users[0].age, 26, "事务提交后年龄更新失败")
            logger.info("事务提交测试完成")

    def test_transaction_rollback(self):
        """
        测试事务回滚
        
        在事务中执行操作，然后引发异常导致回滚：
        1. 插入一条记录
        2. 故意引发异常
        3. 验证记录是否被回滚（不存在）
        
        这个测试确保了在出现错误时，事务能够正确回滚，保持数据一致性。
        """
        logger.info("开始测试事务回滚...")
        try:
            with TransactionManager(self.session) as tm:
                user = Test_Table(name='Charlie', age=35)
                tm.add(user)
                logger.info("事务中插入了一条记录")
                raise Exception("测试事务回滚")
        except Exception as e:
            logger.info(f"事务回滚测试：{str(e)}")

        # 验证回滚结果
        with TransactionManager(self.session) as tm:
            user = tm.query(Test_Table).filter_by(name='Charlie').first()
            self.assertIsNone(user, "事务回滚失败，找到了Charlie的记录")
            logger.info("事务回滚成功，未找到Charlie的记录")

    def test_error_handling(self):
        """
        测试错误处理
        
        尝试执行一些应该失败的操作：
        1. 更新不存在的记录
        2. 删除不存在的记录
        
        这个测试确保系统能够优雅地处理异常情况，而不是崩溃。
        """
        logger.info("开始测试错误处理...")
        with TransactionManager(self.session) as tm:
            # 尝试更新不存在的记录
            non_existent_user = Test_Table(id=9999, name='Not Exist', age=0)
            with self.assertRaises(NoResultFound):
                tm.update(non_existent_user, {'age': 100})
            logger.info("成功捕获更新不存在记录的异常")

            # 尝试删除不存在的记录
            with self.assertRaises(ValueError):
                tm.delete(non_existent_user)
            logger.info("成功捕获删除不存在记录的异常")

if __name__ == "__main__":
    logger.info("开始运行MySQL数据库操作测试...")
    unittest.main(verbosity=2)
    logger.info("所有测试脚本执行完毕，请检查上述输出以确认测试结果。")