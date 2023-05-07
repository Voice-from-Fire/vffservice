from pydantic import BaseModel

from app.db.models import AudioStatus, LabelType


class LabelTypeAndValue(BaseModel):
    label_type: LabelType
    label_value: int


class LabelCreate(BaseModel):
    status: AudioStatus
    labels: list[LabelTypeAndValue]
