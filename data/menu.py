import sqlalchemy
from .db_session import ORMBase


class Menu(ORMBase):
    __tablename__ = 'menu'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    section = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    icon = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ref = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    roles = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    order = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
