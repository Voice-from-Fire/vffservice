from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    Identity,
    Enum,
    String,
    LargeBinary,
    Boolean,
    DateTime,
    Numeric,
    UniqueConstraint,
    JSON,
    CheckConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import EmailType

import enum
import datetime


Base = declarative_base()


@enum.unique
class Role(str, enum.Enum):
    user = "user"
    reviewer = "reviewer"
    moderator = "moderator"
    admin = "admin"


class User(Base):
    __tablename__ = "vff_user"

    id = Column(Integer, Identity(start=10), primary_key=True)

    name = Column(String, nullable=False, unique=True)
    hashed_password = Column(LargeBinary, nullable=False)
    active = Column(Boolean, nullable=False)
    role = Column(Enum(Role), nullable=False)
    email = Column(EmailType)

    extra = Column(JSON)

    samples = relationship("Sample", cascade="all, delete-orphan")
    labels = relationship("Label", cascade="all, delete-orphan")

    def is_moderator_or_more(self) -> bool:
        return self.role == Role.moderator or self.role == Role.admin

    def is_admin(self) -> bool:
        return self.role == Role.admin


@enum.unique
class SampleState(enum.Enum):
    new = "n"
    checked = "c"
    hidden = "h"


class Sample(Base):
    __tablename__ = "sample"

    id = Column(Integer, Identity(start=10), primary_key=True)

    owner = Column(
        Integer,
        ForeignKey("vff_user.id", ondelete="CASCADE"),
        nullable=False,
    )

    duration = Column(Float, nullable=False)

    state = Column(Enum(SampleState), nullable=False, default=SampleState.new)

    labels = relationship("Label", cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", cascade="all, delete-orphan")

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class AudioFile(Base):
    __tablename__ = "audio_file"

    id = Column(Integer, Identity(start=10), primary_key=True)

    sample = Column(
        Integer, ForeignKey("sample.id", ondelete="CASCADE"), nullable=False
    )
    format = Column(String, nullable=False)
    path = Column(String, nullable=False)
    original = Column(Boolean, nullable=False)
    size = Column(Integer, nullable=False)


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

    creator = Column(
        Integer, ForeignKey("vff_user.id", ondelete="CASCADE"), nullable=False
    )
    sample = Column(
        Integer, ForeignKey("sample.id", ondelete="CASCADE"), nullable=False
    )

    status = Column(Enum(AudioStatus), nullable=False)

    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    values = relationship("LabelValue", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("creator", "sample", name="_creator_sample_uc"),)


@enum.unique
class LabelType(enum.Enum):
    gt_gender = "G"
    gender = "g"


class LabelValue(Base):
    __tablename__ = "labelvalue"

    id = Column(Integer, Identity(start=10), primary_key=True)
    sample = Column(Integer, ForeignKey("label.id", ondelete="CASCADE"), nullable=False)

    label_type = Column(Enum(LabelType), nullable=False)
    label_value = Column(JSON(), nullable=False)

    begin_time = Column(Numeric(scale=3))
    end_time = Column(Numeric(scale=3))

    __table_args__ = (
        (
            CheckConstraint(
                "(begin_time IS NULL) = (end_time IS NULL)",
                name="time_null_cc",
            )
        ),
    )


@enum.unique
class EventType(enum.Enum):
    user_new = "user-new"
    user_deleted = "user-del"
    user_deactivated = "user-deac"
    user_role_updated = "user-role-upd"

    sample_new = "sample-new"
    label_new = "label-new"

    error = "error"


class AuditLog(Base):
    __tablename__ = "auditlog"

    id = Column(Integer, Identity(start=10), primary_key=True)

    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    event = Column(Enum(EventType), nullable=False)

    user = Column(Integer)

    sample = Column(Integer)

    label = Column(Integer)

    payload = Column(JSON())
    message = Column(String)
