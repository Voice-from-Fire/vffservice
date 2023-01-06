from sqlalchemy.orm import Session

from app.ops.audit_log import add_audit_log
from ..db import models
from .. import schemas
import bcrypt


def get_user_by_name(db: Session, name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == name).first()


def remove_user(db: Session, user_id: int):
    # TODO: Delete files from storage
    db.query(models.Sample).filter_by(owner=user_id).delete()
    db.query(models.User).filter_by(id=user_id).delete()
    auditLog = add_audit_log(db, event=models.EventType.user_deleted, user=user_id, commit=False)
    db.commit()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    user = models.User(name=user.name, hashed_password=hashed_password, active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    add_audit_log(db, event=models.EventType.user_new, user=user.id, commit=True)
    return user


def check_user_password(user: models.User, password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), user.hashed_password)
