from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.enums import TaskStatus


class TaskCreate(BaseModel):

    title: str

    description: Optional[str] = None

    created_by: int


class TaskUpdate(BaseModel):

    title: Optional[str] = None

    description: Optional[str] = None

    status: Optional[TaskStatus] = None


class TaskAssign(BaseModel):

    assigned_to: int


class TaskResponse(BaseModel):

    id: int

    title: str

    description: Optional[str]

    status: TaskStatus

    created_by: int

    assigned_to: Optional[int]

    created_at: datetime

    updated_at: datetime


    class Config:

        from_attributes = True