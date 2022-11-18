from ..db.models import User, AudioFile
from sqlalchemy.orm import Session
from shutil import copyfileobj
import uuid
import os
import logging
from ..tools import ffmpeg

FILESTORE_PATH = "/data"

logger = logging.Logger(__name__)


def configure_filestore(path: str):
    global FILESTORE_PATH
    FILESTORE_PATH = path


def create_audiofile(db: Session, file, user: User) -> int:
    filename = str(uuid.uuid4()) + ".wav"
    fullpath = os.path.join(FILESTORE_PATH, filename)
    file.seek(0)
    logger.info(f"Uploading file {filename} by {user.name}")
    try:
        with open(fullpath, "wb") as f:
            copyfileobj(file, f)
        duration = ffmpeg.get_duration(fullpath)
        audio_file = AudioFile(filename=filename, duration=duration, owner=user.id)
        db.add(audio_file)
        db.commit()
    except Exception as e:
        logger.info(f"Upload fails, removing file {fullpath}")
        os.unlink(fullpath)
        raise e
    # db.refresh(audio_file)
    return audio_file.id
