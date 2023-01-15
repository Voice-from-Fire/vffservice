from typing import List, Optional

from ..db.models import SampleState, User, AudioFile, Sample, Label, EventType
from app.ops.audit_log import add_audit_log
from sqlalchemy.orm import Session
from shutil import copyfileobj
import uuid
import os
import logging
from ..tools import ffmpeg


FILESTORE_PATH = "/workspace/backend/data"

logger = logging.Logger(__name__)


def configure_filestore(path: str):
    global FILESTORE_PATH
    FILESTORE_PATH = path


def create_sample(db: Session, file, user: User) -> int:
    filename = str(uuid.uuid4())
    fullpath = os.path.join(FILESTORE_PATH, filename)
    tmp_fullpath = fullpath + ".tmp"
    file.seek(0)
    logger.info(f"Uploading file {filename} by {user.name}")
    with open(tmp_fullpath, "wb") as f:
        try:
            copyfileobj(file, f)
            os.rename(tmp_fullpath, fullpath)
            size = os.path.getsize(fullpath)
            duration = ffmpeg.check_and_fix_audio(fullpath)
            sample = Sample(duration=duration, owner=user.id)
            audio_file = AudioFile(path=filename, original=True, size=size)
            sample.audio_files.append(audio_file)
            db.add(sample)
            db.commit()
            add_audit_log(db, event=EventType.sample_new, sample=sample.id, commit=True)
            return sample.id
        except Exception as e:
            logger.info(f"Upload fails, removing file {fullpath}")
            add_audit_log(db, event=EventType.error, message=e, commit=True)
            if os.path.isfile(tmp_fullpath):
                os.unlink(tmp_fullpath)
            os.unlink(fullpath)
            raise e


def get_samples(db: Session, user: User) -> List[Sample]:
    return db.query(Sample).filter(Sample.owner == user.id).all()


def get_sample(db: Session, session_id: int) -> Sample:
    return db.query(Sample).filter(Sample.id == session_id).first()


def get_sample_stream(sample: Sample):
    audio_file: AudioFile = sample.audio_files[0]
    fullpath = os.path.join(FILESTORE_PATH, audio_file.path)
    with open(fullpath, mode="rb") as f:
        yield from f


def get_next_sample_id(db: Session, user: User) -> Optional[int]:
    already_labelled = db.query(Label.sample).filter(Label.creator == user.id)
    not_labelled = db.query(Sample.id).filter(
        Sample.id.not_in(already_labelled), Sample.state != SampleState.hidden
    )
    # db.query(Label.sample).filter(Label.sample.in_(not_labelled)).group_by()
    result = not_labelled.first()
    return result[0] if result else None
