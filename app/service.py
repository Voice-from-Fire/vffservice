from typing import List, Optional
from sqlalchemy.orm import sessionmaker, Session

import app.ops.user as ops_user

from . import schemas
from .db.models import Base
from .db import database
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException


# TODO
APP_SECRET = "todo-load-secret-from-somewhere"

engine = database.connect()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

manager = LoginManager(APP_SECRET, token_url="/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(debug=True)


@app.post("/users", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = ops_user.get_user_by_name(db, user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Name is already used")
    new_user = ops_user.create_user(db, user)
    return new_user


@manager.user_loader(db_provider=get_db)
def load_user(name: str, db: Optional[Session] = None, db_provider=None):
    if db is None:
        db = next(db_provider())
    return ops_user.get_user_by_name(db, name)


@app.post("/auth/token", tags=["users"])
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = load_user(data.username, db=db)
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not ops_user.check_user_password(user, data.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=user.name))
    return {"access_token": access_token}


@app.get("/sample_sets", response_model=List[schemas.SampleSet], tags=["samples"])
def list_sample_sets(user=Depends(manager)):
    pass


@app.get(
    "/sample_sets/{sample_id}", response_model=schemas.SampleSetDetail, tags=["samples"]
)
def sample_set_detail(sample_id: int, user=Depends(manager)):
    pass


@app.get("/label_types", response_model=List[schemas.LabelType], tags=["labels"])
def get_labelling():
    pass


@app.get("/labels/{label_id}", response_model=schemas.Label, tags=["labels"])
def get_label(label_id: int, user=Depends(manager)):
    pass


@app.post("/labels", tags=["labels"])
def create_label(label: schemas.Label, user=Depends(manager)):
    pass


@app.get("/labels/next", response_model=int, tags=["labels"])
def get_next_sample_for_labelling(user=Depends(manager)):
    return 10


@app.get("/audio", tags=["audio"])
def get_own_audiofiles(user=Depends(manager)):
    return []


@app.get("/samples/{sample_id}/audio", tags=["samples"])
def get_audio_data(sample_id: int, user=Depends(manager)):
    pass


@app.post("/audio", tags=["audio"])
async def upload_sample(file: UploadFile, user=Depends(manager)):
    # TODO check size of file
    # TODO check that file is really audio
    # TODO compute hash and check for duplicties
    pass
