from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, Float, Identity, Enum
from sqlalchemy import String, LargeBinary, Boolean, DateTime, Numeric
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

import enum
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "vff_user"

    id = Column(Integer, Identity(start=10), primary_key=True)

    name = Column(String, nullable=False)
    hashed_password = Column(LargeBinary, nullable=False)
    active = Column(Boolean, nullable=False)

    samples = relationship("Sample", cascade="all, delete-orphan")
    sessions = relationship("LabelingSession", cascade="all, delete-orphan")


class Sample(Base):
    __tablename__ = "sample"

    id = Column(Integer, Identity(start=10), primary_key=True)

    owner = Column(
        Integer,
        ForeignKey("vff_user.id", ondelete="CASCADE"),
        nullable=False,
    )

    duration = Column(Float, nullable=False)

    labels = relationship("Label", cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", cascade="all, delete-orphan")


class AudioFile(Base):
    __tablename__ = "audio_file"

    id = Column(Integer, Identity(start=10), primary_key=True)

    sample = Column(
        Integer, ForeignKey("sample.id", ondelete="CASCADE"), nullable=False
    )

    path = Column(String, nullable=False)
    original = Column(Boolean, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class LabelingSession(Base):
    __tablename__ = "label_session"
    id = Column(Integer, Identity(start=10), primary_key=True)
    user = Column(
        Integer, ForeignKey("vff_user.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


@enum.unique
class LabelType(enum.Enum):
    gt_gender = "gt_gender"
    status = "status"
    gender = "gender"


@enum.unique
class AudioStatus(enum.Enum):
    ok = "ok"
    no_audio = "no_audio"
    no_human = "no_human"
    more_speakers = "more_speakers"
    invalid = "invalid"


class Label(Base):
    __tablename__ = "label"

    id = Column(Integer, Identity(start=10), primary_key=True)

    session = Column(
        Integer, ForeignKey("label_session.id", ondelete="CASCADE"), nullable=False
    )
    sample = Column(
        Integer, ForeignKey("sample.id", ondelete="CASCADE"), nullable=False
    )

    label_type = Column(Enum(LabelType), nullable=False)
    label_value = Column(String, nullable=False)

    begin_time = Column(Numeric(scale=3))
    end_time = Column(Numeric(scale=3))

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    deleted_at = Column(DateTime, default=None)
