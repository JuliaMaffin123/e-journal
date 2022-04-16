from sqlalchemy import Column, Integer, String, ForeignKey
from data.db_session import ORMBase
from flask_login import UserMixin


class Users(ORMBase, UserMixin):
    __tablename__ = 'users'
    __json_exclude__ = set(["password"])

    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    otchestvo = Column(String, nullable=True)
    login = Column(String, nullable=True)
    password = Column(String, nullable=True)
    role = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey('classes.cl_id'), nullable=True)
    active = Column(Integer, nullable=True)
