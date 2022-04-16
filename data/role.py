from sqlalchemy import Column, Integer, String
from data.db_session import ORMBase


class Role(ORMBase):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=True)
    start_page = Column(String, nullable=True)
