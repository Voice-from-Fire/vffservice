from typing import List, Optional
from enum import Enum
import datetime
from pydantic import BaseModel

from ..db.models import Language


class Sample(BaseModel):
    id: int
    duration: float
    language: Language
    created_at: Optional[datetime.datetime]  # Can see only moderator
    owner: Optional[int]  # Can see only admin

    size: int
    filename: str

    class Config:
        orm_mode = True


"""
class SampleSet(BaseModel):
    id: int
    name: str
    size: int


class LabelType(BaseModel):
    id: int
    name: str
    help_text: str
    value_labels: List[str]

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Gender",
                "help_text": "Specify how much the voice is masculine or feminine",
                "value_labels": ["male", "female"],
            }
        }


class SampleSetDetail(BaseModel):
    id: int
    name: str
    samples: List[int]
    label_types: List[int]


class LabelInstance(BaseModel):
    label_type: int
    value: float


class LabelCategory(str, Enum):
    ok = "ok"
    no_sound = "no_sound"
    no_human_sound = "no_human_sound"
    more_speakers = "more_speakers"
    other_reason = "other_reason"


class Label(BaseModel):
    id: int | None
    sample_id: int
    user_id: int

    labelling_type: LabelCategory
    labels: List[LabelInstance]
"""
