import imp
import os
import sys
import pytest
import random
import string
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions

TEST_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIRECTORY = os.path.join(TEST_DIRECTORY, "assets")
ROOT_DIRECTORY = os.path.dirname(TEST_DIRECTORY)

sys.path.insert(0, ROOT_DIRECTORY)

from app import config
from userutils import UserService


config.TEST_MODE = True

from app import schemas
from app import service
from app.ops.user import create_user, remove_user
from app.ops.samples import configure_filestore, create_sample
from app.db import database, session as session_module
from app.db.models import Role


TESTUSER_USERNAME = "testuser"
TESTUSER_PASSWORD = "testuserxx"


def random_id(prefix):
    return prefix + "".join(random.choice(string.ascii_lowercase) for _ in range(7))


@pytest.fixture()
def db_session():
    dbname = random_id("testdb")
    original = session_module._get_db

    config.DATABASE_NAME = dbname
    engine, conn = database.init_db()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def my_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    session_module._get_db = my_get_db

    session = SessionLocal()
    yield session
    close_all_sessions()
    conn.execute("commit")
    conn.execute(f"DROP DATABASE {dbname} WITH (FORCE)")
    session_module._get_db = original


@pytest.fixture()
def user(db_session):
    user = create_user(
        db_session,
        schemas.UserCreate(name=TESTUSER_USERNAME, password=TESTUSER_PASSWORD),
    )
    return user


@pytest.fixture()
def admin(db_session):
    user = create_user(
        db_session,
        schemas.UserCreate(name="admin", password=TESTUSER_PASSWORD),
        role=Role.admin,
    )
    return user


@pytest.fixture()
def auth(user, db_session):
    response = service.login(
        data=OAuth2PasswordRequestForm(
            username=user.name, password=TESTUSER_PASSWORD, scope=""
        ),
        db=db_session,
    )
    token = response["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_wav():
    return os.path.join(ASSETS_DIRECTORY, "test.wav")


@pytest.fixture(autouse=True)
def filestorage(tmpdir):
    data_dir = tmpdir / "data"
    data_dir.mkdir()
    configure_filestore(str(data_dir))
    return str(data_dir)


@pytest.fixture()
def sample(db_session, test_wav, user, filestorage):
    with open(test_wav, "rb") as f:
        return create_sample(db_session, f, user)


@pytest.fixture()
def users(db_session):
    return UserService(db_session, service)
