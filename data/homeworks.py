import sqlalchemy
from .db_session import ORMBase
import datetime


class Homeworks(ORMBase):
    __tablename__ = 'homeworks'

    h_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    subject = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    class_num = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    class_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    homework = sqlalchemy.Column(sqlalchemy.String, nullable=True)
