from sqlalchemy import create_engine
from .models import Base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import ProgrammingError
import logging

from .. import config


def connect_db():
    return create_engine(f"{config.DATABASE_URL}/{config.DB_NAME}")


def init_db():
    engine = create_engine(config.DATABASE_URL)
    conn = engine.connect()
    conn.execute("commit")
    try:
        conn.execute(f"create database {config.DB_NAME}")
    except ProgrammingError as e:
        logging.warning("Database already exists.")
        raise e
    engine = connect_db()
    Base.metadata.create_all(engine)
    return engine, conn
