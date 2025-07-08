from pydantic import BaseModel, EmailStr
from typing import List, Optional

from app.application.schemas.task import Task

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: str
    tasks: List[Task] = []

    class Config:
        from_attributes = True 