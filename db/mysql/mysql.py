import config.config as config
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from log.logHelper import get_logger

# 获取日志实例
logger = get_logger()

# 基础声明类，用于创建数据库模型
MySQL_Base = declarative_base()

class MySQL_Database:
    """
    MySQL数据库连接和操作的工具类

    使用说明：
    1. 确保已正确配置MySQL数据库连接参数（在config文件夹下的相应配置文件中）。
    2. 在代码中导入MySQL_Database类：
       from db.mysql.mysql import MySQL_Database

    使用方法：
    1. 实例化数据库工具类：
       db = MySQL_Database()

    2. 获取数据库会话：
       session = db.get_session()

    3. 执行数据库操作，例如：
       # 插入数据
       new_user = User(name="张三", age=30)
       session.add(new_user)
       session.commit()

       # 查询数据
       users = session.query(User).all()
       for user in users:
           print(f"ID: {user.id}, 姓名: {user.name}, 年龄: {user.age}")

    4. 操作完成后，关闭会话：
       db.close_session()

    注意：
    - 确保安装了所有必要的依赖（sqlalchemy, mysql-connector-python等）。
    - 可以参考测试文件来了解更多使用示例。

    测试文件路径：db/mysql/test/test.py
    """

    def __init__(self):
        """
        初始化数据库连接
        - 读取配置文件
        - 创建数据库连接URL
        - 创建数据库引擎
        - 创建会话工厂和全局会话对象
        - 检查并创建表
        """
        try:
            # 读取配置文件
            mysql_config = config.config.get_mysql_config()
            
            # 创建数据库连接URL
            self.database_url = f"mysql+mysqlconnector://{mysql_config['username']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
            
            # 创建数据库引擎，echo=True表示显示SQL语句
            self.engine = create_engine(self.database_url, echo=True)
            
            # 创建会话工厂
            self.SessionFactory = sessionmaker(bind=self.engine)
            
            # 创建一个全局会话对象
            self.Session = scoped_session(self.SessionFactory)
            
            # 检查并创建表
            self.create_tables()
            
            logger.info("MySQL数据库连接成功初始化")
        except Exception as e:
            logger.error(f"MySQL数据库初始化失败: {str(e)}")
            raise

    def create_tables(self):
        """
        检查并创建不存在的表
        """
        try:
            inspector = inspect(self.engine)
            for table_name in MySQL_Base.metadata.tables.keys():
                if not inspector.has_table(table_name):
                    MySQL_Base.metadata.create_all(self.engine)
                    logger.info(f"创建表 {table_name}")
            logger.info("所有必要的表已创建")
        except Exception as e:
            logger.error(f"创建表时发生错误: {str(e)}")
            raise

    def get_session(self):
        """
        获取一个新的数据库会话
        :return: SQLAlchemy会话对象
        """
        return self.Session()

    def close_session(self):
        """
        关闭当前的数据库会话
        """
        self.Session.remove()
        logger.info("数据库会话已关闭")

# 使用示例：
# db = MySQL_Database()
# session = db.get_session()
# 执行数据库操作...
# db.close_session()