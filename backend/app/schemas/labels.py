import datetime
from typing import List
from pydantic import BaseModel

from app.db.models import AudioStatus


class LabelTypeAndValue(BaseModel):
    label_type: str
    label_value: int

    class Config:
        orm_mode = True


class LabelCreate(BaseModel):
    status: AudioStatus
    values: List[LabelTypeAndValue]
    version: int


class Label(BaseModel):
    id: int
    creator: int
    sample: int
    status: AudioStatus
    version: int
    created_at: datetime.datetime
    values: List[LabelTypeAndValue]

    class Config:
        orm_mode = True
