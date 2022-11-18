import os
import sys
import pytest
import random
import string
from fastapi.security import OAuth2PasswordRequestForm


TEST_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIRECTORY = os.path.join(TEST_DIRECTORY, "assets")
ROOT_DIRECTORY = os.path.dirname(TEST_DIRECTORY)

sys.path.insert(0, ROOT_DIRECTORY)


from app import schemas
from app.service import get_db, login
from app.ops.user import create_user, remove_user
from app.ops.audiofiles import configure_filestore


TESTUSER_PASSWORD = "testuserxx"


@pytest.fixture(scope="session")
def db_session():
    yield from get_db()


@pytest.fixture()
def user(db_session):
    username = "testuserxx" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    user = create_user(
        db_session, schemas.UserCreate(name=username, password=TESTUSER_PASSWORD)
    )
    yield user
    remove_user(db_session, user.id)


@pytest.fixture()
def auth(user, db_session):
    response = login(
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
