from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from data.db_session import ORMBase


class Homeworks(ORMBase):
    __tablename__ = 'homeworks'

    h_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    date = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey('classes.cl_id'), nullable=True)
    homework = Column(String, nullable=True)
