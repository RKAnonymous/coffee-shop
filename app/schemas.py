from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str]
    last_name: Optional[str]

class UserRead(BaseModel):
    id: int
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    is_verified: bool
    role: str

    model_config = {
        "from_attributes": True
    }

class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class UserUpdateRole(BaseModel):
    role: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class VerifySchema(BaseModel):
    email: EmailStr
    code: str
