import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


class ORMBase(object):
    def __json__(self):
        json_exclude = getattr(self, '__json_exclude__', set())
        return {key: value for key, value in self.__dict__.items()
                # Do not serialize 'private' attributes
                # (SQLAlchemy-internal attributes are among those, too)
                if not key.startswith('_')
                and key not in json_exclude}


ORMBase = dec.declarative_base(cls=ORMBase)

# Фабрика подключений
__factory = None


# создает orm
def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    # Ссылка на базу данных
    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    # print(f"Подключение к базе данных по адресу {conn_str}")

    # Подключаем БД
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import models

    ORMBase.metadata.create_all(engine)


# инициализация библиотеки
def create_session():
    global __factory
    return __factory()
