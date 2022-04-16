from sqlalchemy import Column, Integer, String, ForeignKey
from data.db_session import ORMBase


class Grade(ORMBase):
    __tablename__ = 'grades'

    g_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    date = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    grade = Column(Integer, nullable=True)
    reason = Column(String, nullable=True)
