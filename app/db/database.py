from sqlalchemy import create_engine
from .models import Base
from sqlalchemy_utils import database_exists, create_database

DATABASE_NAME = "voicedb"


def connect():
    return create_engine(f"postgresql+psycopg2://postgres:postgres@db/{DATABASE_NAME}")


def init_db():
    engine = create_engine("postgresql+psycopg2://postgres:postgres@db")
    conn = engine.connect()
    conn.execute("commit")
    conn.execute(f"create database {DATABASE_NAME}")
    engine = connect()
    Base.metadata.create_all(engine)
