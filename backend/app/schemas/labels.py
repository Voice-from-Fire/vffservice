import datetime
from typing import List
from pydantic import BaseModel

from app.db.models import AudioStatus, LabelType


class LabelTypeAndValue(BaseModel):
    label_type: LabelType
    label_value: int

    class Config:
        orm_mode = True


class LabelCreate(BaseModel):
    status: AudioStatus
    values: List[LabelTypeAndValue]


class Label(BaseModel):
    id: int
    creator: int
    sample: int
    status: AudioStatus
    created_at: datetime.datetime
    values: List[LabelTypeAndValue]

    class Config:
        orm_mode = True
