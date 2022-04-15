import sqlalchemy
from sqlalchemy import null
from flask_login import UserMixin
from .db_session import ORMBase
import sqlalchemy.orm as orm


class Users(ORMBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    otchestvo = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.cl_id'), nullable=True)
    active = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    # cls = orm.relation('Classes', backref='students')