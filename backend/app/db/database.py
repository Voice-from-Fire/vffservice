from sqlalchemy import create_engine
from .models import Base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import ProgrammingError
import logging

DATABASE_NAME = "voicedb"


def connect():
    return create_engine(f"postgresql+psycopg2://postgres:postgres@db/{DATABASE_NAME}")


def init_db():
    engine = create_engine("postgresql+psycopg2://postgres:postgres@db")
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute(f"create database {DATABASE_NAME}")
    except ProgrammingError:
        logging.warning("Database already exists.")
    engine = connect()
    Base.metadata.create_all(engine)
