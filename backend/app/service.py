from datetime import timedelta
from typing import List, Optional
from app.schemas.labels import LabelCreate
from httpcore import request
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import os
import os.path

import app.ops.user as ops_user
import app.ops.samples as ops_samples
import app.ops.labels as ops_labels
from .tools.ffmpeg import MIMETYPES, convert_to_mp3
from .schemas.user import UserPasswordUpdate
from .auth import can_access_sample
from .ops.auditlog import add_audit_log
from .config import DB_HOST
from . import schemas
from .db.session import get_db
from .db.models import (
    AudioStatus,
    AuditLog,
    Base,
    EventType,
    Label,
    User,
    Role,
)
from .db.models import AuditLog, Base, EventType, User, Role
from .db import database
from fastapi import Depends, FastAPI, HTTPException, UploadFile, Form, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi_login import LoginManager
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

logger.info("DB_HOST = %s", DB_HOST)

# TODO
APP_SECRET = "todo-load-secret-from-somewhere"

# In client, I have problem with DioError, at least in WEB backend, I cannot read HTTP error code,
# and therefore detect if session is timeouted, I connect silently ask for new token,
# temporary solution is to make expiration very long.
manager = LoginManager(
    APP_SECRET, token_url="/auth/token", default_expiry=timedelta(hours=12)
)


origins = [
    "*",
]

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users", response_model=List[schemas.User], tags=["users"])
def get_all_users(user: User = Depends(manager), db: Session = Depends(get_db)):
    if not user.is_moderator_or_more():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    return ops_user.get_all_users(db)


@app.get("/users/summaries", response_model=List[schemas.UserSummary], tags=["users"])
def get_all_user_summaries(
    user: User = Depends(manager), db: Session = Depends(get_db)
):
    if not user.is_moderator_or_more():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    return ops_user.get_all_user_summaries(db)


@app.get("/users/{user_id}", response_model=schemas.User, tags=["users"])
def get_user(
    user_id: int, user: User = Depends(manager), db: Session = Depends(get_db)
):
    if not user.is_moderator_or_more():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    return ops_user.get_user_by_id(db, user_id)


@app.post("/users", response_model=schemas.User, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = ops_user.get_user_by_name(db, user.name)
    if db_user:
        raise HTTPException(status_code=409, detail="Name is already used")

    invitation_codes = os.environ.get("VFF_INVITATION_CODES", "").split()

    if invitation_codes:
        if user.invitation_code not in invitation_codes:
            raise HTTPException(status_code=401, detail="Invalid invitation code")
        extra = {"invitation": user.invitation_code}
        if user.invitation_code.endswith("-a"):
            role = Role.admin
        elif user.invitation_code.endswith("-m"):
            role = Role.moderator
        elif user.invitation_code.endswith("-r"):
            role = Role.reviewer
        elif user.invitation_code.endswith("-u"):
            role = Role.user
        else:
            role = Role.reviewer
    else:
        extra = None
        role = Role.user
    new_user = ops_user.create_user(db, user, extra=extra, role=role)
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
    if (
        not user.is_moderator_or_more()
        or
        # moderator cannot deactivate admin
        db_user is not None
        and Role.admin == db_user.role
        and not user.is_admin()
    ):
        raise HTTPException(status_code=403, detail="Unauthorized request")
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User id {} does not exist, user cannot be deactivated.".format(
                user_id
            ),
        )
    if db_user.id == user.id:
        raise HTTPException(status_code=403, detail="User cannot deactivate themselves")
    ops_user.deactivate_user(db, db_user)


@app.patch("/users/password", tags=["users"])
def update_password(
    target: UserPasswordUpdate,
    user: User = Depends(manager),
    db: Session = Depends(get_db),
):
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    target_user = ops_user.get_user_by_id(db, target.id)
    if target_user is None:
        raise HTTPException(
            status_code=404, detail="User id {} does not exist".format(target.id)
        )
    logger.info("User %s changes password of %s", user.name, target_user.name)
    ops_user.update_password(db, target_user, target.password)


@app.patch("/users/role_update", response_model=schemas.User, tags=["users"])
def update_role(
    update: schemas.UserRoleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(manager),
):
    if not user.is_admin():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    db_user = ops_user.get_user_by_id(db, update.id)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="User id {} does not exist, role cannot be updated.".format(
                update.id
            ),
        )
    if db_user.id == user.id:
        raise HTTPException(status_code=403, detail="User cannot update their role")
    return ops_user.update_role(db, db_user, update.role)


@app.post("/auth/token", tags=["users"])
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = load_user(data.username, db=db)
    if not user or not user.active:
        raise InvalidCredentialsException
    elif not ops_user.check_user_password(user, data.password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data=dict(sub=user.name))
    return {"access_token": access_token, "user": schemas.User.from_orm(user)}


# !!! language does not have Language because of typescript openapi generator
# is broken and generates wrong code when enum is top level value
@app.post("/samples", response_model=int, tags=["samples"])
def upload_sample(
    language: str = Form(),
    file: UploadFile = File(),
    user=Depends(manager),
    db: Session = Depends(get_db),
):
    if language not in ("NV", "XX", "en", "cs"):
        raise HTTPException(status_code=422, detail="Invalid language")
    # TODO check size of file
    # TODO compute hash and check for duplicties
    return ops_samples.create_sample(db, file.file, user, language)


@app.get("/samples", response_model=List[schemas.Sample], tags=["samples"])
def get_own_samples(user=Depends(manager), db: Session = Depends(get_db)):
    return ops_samples.get_samples(db, user)


# This method has to be before `get_sample`
@app.get("/samples/next", response_model=Optional[schemas.Sample], tags=["samples"])
def get_next_sample_for_labelling(
    user: User = Depends(manager), db: Session = Depends(get_db)
):
    sample = ops_samples.get_next_sample(db, user)
    if sample is not None:
        return sample.anonymize()
    else:
        return None


@app.get("/samples/{sample_id}", response_model=schemas.Sample, tags=["samples"])
def get_sample(sample_id: int, user=Depends(manager), db: Session = Depends(get_db)):
    sample = ops_samples.get_sample(db, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    if sample.owner != user.id:
        raise HTTPException(status_code=401)
    return sample


@app.delete("/samples/{sample_id}", tags=["samples"])
def delete_sample(sample_id: int, user=Depends(manager), db: Session = Depends(get_db)):
    sample = ops_samples.get_sample(db, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    if sample.owner != user.id:
        raise HTTPException(status_code=401)
    ops_samples.delete_sample(db, sample)
    return "ok"  # For flutter OpenAPI generator


@app.get("/sample/{sample_id}/{key}/audio", tags=["audio"])
def get_original_audio(sample_id: int, key: str, db: Session = Depends(get_db)):
    sample = ops_samples.get_sample(db, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    if key != sample.filename[:5]:
        raise HTTPException(status_code=401, detail="Cannot access this file")
    # if not can_access_sample(user, sample):
    #    raise HTTPException(status_code=401, detail="You cannot access this file")
    stream = ops_samples.get_file_stream(sample.filename)
    if stream is None:
        raise HTTPException(status_code=404, detail="File not found")

    def streamer():
        with stream:
            yield from stream

    mime_type = MIMETYPES.get(sample.format) or "application/octet-stream"
    return StreamingResponse(streamer(), media_type=mime_type)


@app.get("/sample/{sample_id}/{key}/mp3", tags=["audio"])
def get_mp3_audio(sample_id: int, key: str, db: Session = Depends(get_db)):
    sample = ops_samples.get_sample(db, sample_id)
    if sample is None:
        raise HTTPException(status_code=404, detail="Sample not found")
    if key != sample.filename[:5]:
        raise HTTPException(status_code=401, detail="Cannot access this file")
    # if not can_access_sample(user, sample):
    #    raise HTTPException(status_code=401, detail="You cannot access this file")
    stream = ops_samples.get_file_stream(sample.filename)
    if stream is None:
        raise HTTPException(status_code=404, detail="File not found")
    with stream:
        data = stream.read()
    if sample.format != "mp3":
        data = convert_to_mp3(data)
    return HTMLResponse(data, media_type="audio/mp3")


@app.get(
    "/samples/owner/{user_id}", response_model=List[schemas.Sample], tags=["samples"]
)
def get_samples_of_user(
    user_id: int, user: User = Depends(manager), db: Session = Depends(get_db)
):
    if not user.is_moderator_or_more():
        raise HTTPException(status_code=403, detail="Unauthorized request")
    found_user = ops_user.get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return ops_samples.get_samples(db, found_user)


@app.post("/samples/{sample_id}/label", response_model=int, tags=["labels"])
def create_label(
    sample_id: int,
    label: LabelCreate,
    user: User = Depends(manager),
    db: Session = Depends(get_db),
):
    assert label.version == 0
    try:
        return ops_labels.create_label(db, label, user, sample_id, label.version)
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="The user already created a label for this sample."
        )


@app.get(
    "/samples/{sample_id}/labels", response_model=List[schemas.Label], tags=["labels"]
)
def get_labels_for_sample(
    sample_id: int, user: User = Depends(manager), db: Session = Depends(get_db)
):
    if not user.is_admin() and not ops_labels.is_owner(db, user, sample_id):
        raise HTTPException(status_code=403, detail="Unauthorized request")
    return ops_labels.get_labels_for_sample(db, sample_id)


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
