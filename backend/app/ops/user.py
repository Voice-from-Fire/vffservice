from sqlalchemy.orm import Session
from typing import List

from app.ops.audit_log import add_audit_log
from ..db import models
from .. import schemas
import bcrypt


def get_user_by_name(db: Session, name: str) -> models.User:
    return db.query(models.User).filter(models.User.name == name).first()


def get_user_by_id(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()


def remove_user(db: Session, user_id: int):
    # TODO: Delete files from storage
    db.query(models.Sample).filter_by(owner=user_id).delete()
    db.query(models.User).filter_by(id=user_id).delete()
    auditLog = add_audit_log(
        db, event=models.EventType.user_deleted, user=user_id, commit=False
    )
    db.commit()


def create_user(
    db: Session, user: schemas.UserCreate, *, role: models.Role = models.Role.uploader
) -> models.User:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), salt)
    user = models.User(
        name=user.name, hashed_password=hashed_password, role=role, active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    add_audit_log(db, event=models.EventType.user_new, user=user.id, commit=True)
    return user


def check_user_password(user: models.User, password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), user.hashed_password)


def deactivate_user(db: Session, user: models.User):
    user.active = False
    auditLog = add_audit_log(
        db, event=models.EventType.user_deactivated, user=user.id, commit=False
    )
    db.commit()


def update_role(db: Session, user: models.User, role: models.Role) -> models.User:
    user.role = role
    auditLog = add_audit_log(
        db, event=models.EventType.user_role_updated, user=user.id, commit=False
    )
    db.commit()
    return user
