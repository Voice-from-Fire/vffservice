from typing import Optional
from pydantic import BaseModel, constr, EmailStr

from app.db.models import Role


class UserCreate(BaseModel):
    name: constr(regex="^[a-zA-Z0-9]{3,30}$")
    email: Optional[EmailStr]
    password: str
    invitation_code: Optional[str]


class UserRoleUpdate(BaseModel):
    id: int
    role: Role


class UserPasswordUpdate(BaseModel):
    id: int
    password: str


class User(BaseModel):
    id: int
    name: str
    role: Role

    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    user: User
    samples_count: int
    labels_count: int
