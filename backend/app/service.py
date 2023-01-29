from typing import List, Optional
from httpcore import request
from sqlalchemy.orm import sessionmaker, Session

import app.ops.user as ops_user
import app.ops.samples as ops_samples
from app.ops.audit_log import add_audit_log

from . import schemas
from .db.models import AuditLog, Base, EventType, User, Role
from .db import database
from .db.session import get_db
from fastapi import Depends, FastAPI, HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse


# TODO
APP_SECRET = "todo-load-secret-from-somewhere"

manager = LoginManager(APP_SECRET, token_url="/auth/token")

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.patch("/users/{user_id}/deactivate", tags=["users"])
def deactivate_user(
    user_id: int, db: Session = Depends(get_db), user: User = Depends(manager)
):
    db_user = ops_user.get_user_by_id(db, user_id)
    if db_user is not None:
        if not user.is_moderator_or_more() or (
            # moderator cannot deactivate admin
            Role.admin == db_user.role
            and not user.is_admin()
        ):
            raise HTTPException(status_code=403, detail="Unauthorized request")
    else:
        raise HTTPException(
            status_code=404,
            detail="User id {} does not exist, user cannot be deactivated.".format(
                user_id
            ),
        )
    if user.is_admin() and db_user.id == user.id:
        raise HTTPException(
            status_code=403, detail="Admin user cannot deactivate themselves"
        )
    ops_user.deactivate_user(db, db_user)


@app.patch("/users/role_update", tags=["users"])
def update_role(
    request: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(manager),
):
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    db_user = ops_user.get_user_by_id(db, request.id)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User id {} does not exist, role cannot be updated.".format(
                request.id
            ),
        )
    if user.is_admin() and db_user.id == user.id:
        raise HTTPException(
            status_code=403, detail="Admin user cannot update their role"
        )
    return ops_user.update_role(db, db_user, user.role)


@app.post("/auth/token", tags=["users"])
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = load_user(data.username, db=db)
    if not user or not user.active:
        raise InvalidCredentialsException
    elif not ops_user.check_user_password(user, data.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=user.name))
    return {"access_token": access_token}


@app.get("/users", response_model=List[schemas.User], tags=["users"])
def get_all_users(user: User = Depends(manager), db: Session = Depends(get_db)):
    if user.is_moderator_or_more():
        return ops_user.get_users(db)
    raise HTTPException(status_code=403, detail="Unauthorized request")


@app.post("/samples", response_model=int, tags=["samples"])
async def upload_sample(
    file: UploadFile, user=Depends(manager), db: Session = Depends(get_db)
):
    # TODO check size of file
    # TODO check that file is really audio
    # TODO compute hash and check for duplicties
    return ops_samples.create_sample(db, file.file, user)


@app.get("/samples", response_model=List[schemas.Sample], tags=["samples"])
def get_own_samples(user=Depends(manager), db: Session = Depends(get_db)):
    return ops_samples.get_samples(db, user)


@app.get("/samples/{sample_id}/audio", tags=["samples"])
def get_audio(sample_id: int, user=Depends(manager), db: Session = Depends(get_db)):
    sample = ops_samples.get_sample(db, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    if sample.owner != user.id:
        raise HTTPException(status_code=402)
    stream = ops_samples.get_sample_stream(sample)
    return StreamingResponse(stream)


@app.get("/samples/next", response_model=Optional[int], tags=["samples"])
def get_next_sample_for_labelling(
    user: User = Depends(manager), db: Session = Depends(get_db)
):
    return ops_samples.get_next_sample_id(db, user)


@app.get(
    "/samples/owner/{user_id}", response_model=List[schemas.Sample], tags=["samples"]
)
def get_samples_of_user(
    user_id: int, user: User = Depends(manager), db: Session = Depends(get_db)
):
    if user.is_moderator_or_more():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    found_user = ops_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return ops_samples.get_samples(db, found_user)


"""
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


@app.get("/samples/{sample_id}/audio", tags=["samples"])
def get_audio_data(sample_id: int, user=Depends(manager)):
    pass
"""
