import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

ORMBase = dec.declarative_base()

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
