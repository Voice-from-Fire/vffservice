from typing import List, Optional
from enum import Enum
import datetime
from pydantic import BaseModel


class Sample(BaseModel):
    id: int
    duration: float
    language: str
    created_at: Optional[datetime.datetime]  # Can see only moderator
    owner: Optional[int]  # Can see only admin

    size: int
    filename: str

    class Config:
        orm_mode = True