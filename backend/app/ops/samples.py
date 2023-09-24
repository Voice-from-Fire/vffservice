from typing import List, Optional

from ..db.models import User, Sample, Label, EventType
from .. import config
from .auditlog import add_audit_log
from sqlalchemy.orm import Session
from shutil import copyfileobj
import uuid
import os
import logging
from ..tools import ffmpeg
from . import storage
import tempfile


logger = logging.Logger(__name__)


def create_sample(
    db: Session, file, user: User, language: str, comment: str | None = None
) -> int:
    logger.info(f"Getting sample from user {user.id}")
    filename = str(uuid.uuid4()).replace("-", "")
    file.seek(0)
    logger.info(f"Uploading file {filename} by {user.name}")
    with tempfile.NamedTemporaryFile() as f:
        try:
            copyfileobj(file, f)
            f.flush()
            size = os.path.getsize(f.name)
            format, duration = ffmpeg.check_and_fix_audio(
                f.name, do_not_check=False  # user.name == "Evelyn"
            )
            storage.instance.upload_filename(f.name, filename)
            sample = Sample(
                duration=duration,
                owner=user.id,
                language=language,
                size=size,
                format=format,
                filename=filename,
                hidden_comment=comment,
            )
            db.add(sample)
            db.commit()
            add_audit_log(db, event=EventType.sample_new, sample=sample.id, commit=True)
            return sample.id
        except Exception as e:
            logger.info(f"Upload fails {e}")
            add_audit_log(db, event=EventType.error, message=str(e), commit=True)
            raise e


def delete_sample(db: Session, sample: Sample):
    logger.info("Removing sample %s", sample.id)
    path = sample.filename
    assert not os.path.isabs(path)
    logger.info("Removing file %s", path)
    storage.instance.delete(path)
    db.delete(sample)
    db.commit()


def get_samples(db: Session, user: User) -> List[Sample]:
    return db.query(Sample).filter(Sample.owner == user.id).all()


def get_sample(db: Session, sample_id: int) -> Sample:
    return db.query(Sample).filter(Sample.id == sample_id).first()


def get_file_stream(filename: str):
    return storage.instance.open(filename)


def get_next_sample(db: Session, user: User) -> Optional[Sample]:
    already_labelled = db.query(Label.sample).filter(Label.creator == user.id)
    not_labelled = db.query(Sample).filter(
        Sample.id.not_in(already_labelled), Sample.dataset.is_(None)
    )
    # db.query(Label.sample).filter(Label.sample.in_(not_labelled)).group_by()
    return not_labelled.first()
