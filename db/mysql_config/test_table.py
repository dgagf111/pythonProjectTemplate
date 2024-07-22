from sqlalchemy import Column, Integer, String
from mysql_config.mysql import MySQL_Base

class Test_Table(MySQL_Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)