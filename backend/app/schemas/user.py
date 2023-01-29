from pydantic import BaseModel, constr

from app.db.models import Role


class UserCreate(BaseModel):
    name: constr(regex="^[a-zA-Z0-9]{3,30}$")
    password: str

class UserRoleUpdate(BaseModel):
    id: int
    role: Role

class User(BaseModel):
    id: int
    name: str
    role: Role

    class Config:
        orm_mode = True
