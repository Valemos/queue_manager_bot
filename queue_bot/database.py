from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

_engine = create_engine('sqlite:///:memory:', echo=True)
db_session = sessionmaker(bind=_engine)


def init_database():
    Base.metadata.create_all(_engine)


def reset_database():
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)
