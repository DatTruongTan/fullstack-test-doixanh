from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[Literal["low", "normal", "high"]] = None

class TaskCreate(TaskBase):
    title: str
    due_date: datetime = datetime.now()
    priority: Literal["low", "normal", "high"] = "normal"

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    due_date: datetime
    priority: Literal["low", "normal", "high"]

    class Config:
        from_attributes = True 