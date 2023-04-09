import imp
import os
import shutil
import sys
import pytest
import random
import string
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker, Session, close_all_sessions
from sqlalchemy_utils.functions import create_database, drop_database

os.environ["DB_TYPE"] = "direct"
os.environ["STORAGE_TYPE"] = "local"
os.environ["DB_HOST"] = "db"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASSWORD"] = "postgres"
os.environ["DB_NAME"] = "voicedb"

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
from app.ops.samples import create_sample
from app.ops.storage import configure_filestore
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

    config.DB_NAME = dbname
    url = config.update_db_url()
    create_database(url)
    engine = database.init_db()
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
    drop_database(url)
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


def make_local_asset(tmpdir, filename):
    source = os.path.join(ASSETS_DIRECTORY, filename)
    target_dir = tmpdir / "assets"
    os.makedirs(target_dir, exist_ok=True)
    target = str(target_dir / filename)
    shutil.copyfile(source, target)
    return target


@pytest.fixture()
def test_wav(tmpdir):
    return make_local_asset(tmpdir, "test.wav")


@pytest.fixture()
def test_webm(tmpdir):
    return make_local_asset(tmpdir, "test.webm")


@pytest.fixture()
def test_ogg(tmpdir):
    return make_local_asset(tmpdir, "test.ogg")


@pytest.fixture(autouse=True)
def filestorage(tmpdir):
    data_dir = tmpdir / "data"
    data_dir.mkdir()
    configure_filestore(str(data_dir))
    return str(data_dir)


@pytest.fixture()
def sample(db_session, test_wav, user, filestorage):
    with open(test_wav, "rb") as f:
        return create_sample(db_session, f, user, "en")


@pytest.fixture()
def users(db_session):
    return UserService(db_session, service)
