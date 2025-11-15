from pythonprojecttemplate.config.config import config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from pythonprojecttemplate.log.logHelper import get_logger

# 获取日志实例
logger = get_logger()

# 基础声明类，用于创建数据库模型
MySQL_Base = declarative_base()

class MySQL_Database:
    def __init__(self):
        self.engine = self._create_engine()
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self.create_tables()

    def _create_engine(self):
        mysql_config = config.get_mysql_config()
        connection_string = f"mysql+pymysql://{mysql_config['username']}:{mysql_config['password']}@{mysql_config['host']}:{mysql_config['port']}/{mysql_config['database']}"
        return create_engine(
            connection_string,
            isolation_level="READ COMMITTED",
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600
        )

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