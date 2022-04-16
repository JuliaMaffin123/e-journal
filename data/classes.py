from sqlalchemy import Column, String, Integer, Text
from data.db_session import ORMBase


class Classes(ORMBase):
    __tablename__ = 'classes'

    cl_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    number = Column(Integer, nullable=True)
    letter = Column(String, nullable=True)
    schedule = Column(Text, nullable=True)
    time_schedule = Column(Text, nullable=True)
