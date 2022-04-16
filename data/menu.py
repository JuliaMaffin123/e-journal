from sqlalchemy import Column, Integer, String
from data.db_session import ORMBase


class Menu(ORMBase):
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=True)
    section = Column(String, nullable=True)
    title = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    ref = Column(String, nullable=True)
    roles = Column(String, nullable=True)
    order = Column(Integer, nullable=True)
