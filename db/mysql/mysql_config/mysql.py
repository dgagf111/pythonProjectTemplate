import config 
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import config.config

# 基础声明类
MySQL_Base = declarative_base()

class MySQL_Database:
    def __init__(self, ):
        # 读取配置文件
        MySql = config.config.get_MySQL_config()
        
        username = MySql['username']
        password = MySql['password']
        host = MySql['host']
        port = MySql['port']
        database = MySql['database']

        # 创建数据库连接URL
        self.database_url = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
        # 创建数据库引擎
        self.engine = create_engine(self.database_url, echo=True)
        # 创建会话工厂
        self.SessionFactory = sessionmaker(bind=self.engine)
        # 创建一个全局会话对象
        self.Session = scoped_session(self.SessionFactory)
        # 检查并创建表
        self.create_tables()

    # 创建不存在的表
    def create_tables(self):
        inspector = inspect(self.engine)
        for table_name in MySQL_Base.metadata.tables.keys():
            if not inspector.has_table(table_name):
                MySQL_Base.metadata.create_all(self.engine)

    def get_session(self):
        # 获取一个会话
        return self.Session()

    def close_session(self):
        # 关闭会话
        self.Session.remove()