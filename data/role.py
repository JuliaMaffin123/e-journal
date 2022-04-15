import sqlalchemy
from .db_session import ORMBase


class Role(ORMBase):
    __tablename__ = 'role'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_page = sqlalchemy.Column(sqlalchemy.String, nullable=True)
