from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer, Float, Identity
from sqlalchemy import String, LargeBinary
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "vff_user"

    id = Column(Integer, Identity(start=10), primary_key=True)
    name = Column(String)
    hashed_password = Column(LargeBinary)


class AudioFile(Base):
    __tablename__ = "audio_file"

    name = Column(String, primary_key=True)
    duration = Column(Float)


class SampleSet(Base):
    __tablename__ = "sample_set"

    id = Column(Integer, Identity(start=100), primary_key=True)
    name = Column(String)
    samples = relationship("Sample")


class Sample(Base):
    __tablename__ = "sample"

    id = Column(Integer, Identity(start=100), primary_key=True)
    start = Column(Float)
    duration = Column(Float)
    audio_file = Column(String, ForeignKey("audio_file.name"))
    sample_set_id = Column(Integer, ForeignKey("sample_set.id"))
