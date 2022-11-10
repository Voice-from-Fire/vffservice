from typing import List
from sqlalchemy.orm import sessionmaker, Session
from .models import Base
from . import database, schemas, user_ops
from fastapi import Depends, FastAPI, HTTPException
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


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_ops.get_user_by_name(db, user.name)
    if db_user:
        raise HTTPException(status_code=400, detail="Name is already used")
    new_user = user_ops.create_user(db, user)
    return new_user


@manager.user_loader()
def load_user(name: str, db: Session):
    return user_ops.get_user_by_name(db, name)


@app.post("/auth/token")
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = load_user(data.username, db)
    if not user:
        raise InvalidCredentialsException  # you can also use your own HTTPException
    elif not user_ops.check_user_password(user, data.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=user.name))
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/sample_sets", response_model=List[schemas.SampleSet])
def list_sample_sets():
    pass


@app.get("/sample_sets/{sample_id}", response_model=schemas.SampleSetDetail)
def sample_set_detail(sample_id: int):
    pass


@app.get("/label_types", response_model=List[schemas.LabelType])
def get_labelling():
    pass


@app.get("/labels/{label_id}", response_model=schemas.Label)
def get_label(label_id: int):
    pass


@app.post("/labels")
def create_label(label: schemas.Label):
    pass


@app.get("/sample/{sample_id}/audio")
def get_audio_data(sample_id: int):
    pass
