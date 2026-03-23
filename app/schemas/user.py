# app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)  # ... 代表本项必填
    email: Optional[EmailStr] = None
    role: str = Field(..., pattern="^(admin|underwriter)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserOut(UserBase):
    id: int
    is_active: bool = True

    model_config = ConfigDict (from_attributes = True)  # 允许从 ORM 对象转换，把一个数据库对象变成 JSON


class UserInDB(UserOut):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

