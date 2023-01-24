from typing import Optional
from pydantic import BaseModel, constr


class UserCreate(BaseModel):
    name: constr(regex="^[a-zA-Z0-9]{3,30}$")
    password: str
    invitation_code: Optional[str]


class User(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
