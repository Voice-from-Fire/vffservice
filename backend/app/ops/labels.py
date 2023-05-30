from sqlalchemy import JSON
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
import json

from app.schemas.labels import LabelCreate

from ..db.models import (
    LabelValue,
    User,
    Sample,
    Label,
    AudioStatus,
    LabelType,
    EventType,
    AudioStatus,
)
from typing import Any, List
import logging
from sqlalchemy.orm import Session
from .. import schemas
from .auditlog import add_audit_log


logger = logging.getLogger(__name__)


def create_label(
    db: Session, label_create: LabelCreate, user: User, sample_id: int
) -> int:
    label: Label = Label(creator=user.id, sample=sample_id, status=label_create.status)
    label.values = [
        LabelValue(label_type=label.label_type, label_value=label.label_value)
        for label in label_create.values
    ]
    try:
        db.add(label)
        db.commit()
        add_audit_log(db, event=EventType.label_new, label=label.id, commit=True)
        return label.id
    except IntegrityError as e:
        logger.info(
            f"User {user.id} is trying to create a duplicated label for sample {sample_id} - {e}"
        )
        raise e


def get_labels_for_sample(db: Session, sample_id: int) -> List[Label]:
    return (
        db.query(Label)
        .options(selectinload(Label.values))
        .filter(Label.sample == sample_id)
        .all()
    )


def delete_labels_for_sample(db: Session, sample_id: int):
    logger.info("Removing labels for sample %s", sample_id)
    db.query(Label).filter(Label.sample == sample_id).delete()
    db.commit()


def is_owner(db: Session, user: User, sample_id: int) -> bool:
    sample: Sample = db.query(Sample).filter(Sample.id == sample_id).first()
    return sample.owner == user.id
