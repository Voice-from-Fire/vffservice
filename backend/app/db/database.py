from sqlalchemy import create_engine
from .models import Base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import ProgrammingError
import logging

from .. import config


if config.RUN_ENVIRONMENT == "gcloud":
    from google.cloud.sql.connector import Connector, IPTypes

    connector = Connector()


def connect_db(use_database=True):

    if config.RUN_ENVIRONMENT == "gcloud":

        def get_conn():
            return connector.connect(
                config.DB_HOST,
                "pg8000",
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                db=config.DB_NAME if use_database else None,
                ip_type=IPTypes.PUBLIC,
            )

        return create_engine(
            "postgresql+pg8000://",
            creator=get_conn,
        )
    else:
        if use_database:
            return create_engine(f"{config.DATABASE_URL}/{config.DB_NAME}")
        else:
            return create_engine(config.DATABASE_URL)


def init_db():
    engine = connect_db(use_database=False)
    conn = engine.connect()
    conn.execute("commit")
    try:
        print(f"Creating database {config.DB_NAME}")
        conn.execute(f"create database {config.DB_NAME}")
    except ProgrammingError as e:
        logging.warning("Database already exists.")
        raise e
    engine = connect_db()
    Base.metadata.create_all(engine)
    return engine, conn
