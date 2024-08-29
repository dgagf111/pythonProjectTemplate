from sqlalchemy import Column, Integer, String
from db.mysql.mysql import MySQL_Base

class Test_Table(MySQL_Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Test_Table(id={self.id}, name='{self.name}', age={self.age})>"