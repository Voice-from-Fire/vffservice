from sqlalchemy.orm import sessionmaker

from .database import connect_db
from .models import Base

from .. import config

if config.TEST_MODE:

    def _get_db():
        raise Exception("Need to be overriden by test framework")

    def get_db():
        yield from _get_db()

else:
    engine = connect_db()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
