import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


_database_url = os.environ['DATABASE_URL']

_database_engine = create_engine(_database_url)
SessionFactory = sessionmaker(_database_engine)

Base = declarative_base()


def create_all_tables():
    Base.metadata.create_all(_database_engine)


def drop_all_tables():
    Base.metadata.drop_all(_database_engine)
