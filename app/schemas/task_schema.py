from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.enums import TaskStatus


class TaskCreate(BaseModel):

    title: str

    description: Optional[str] = None

    created_by: int
    assigned_to: Optional[int] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING


class TaskUpdate(BaseModel):

    title: Optional[str] = None

    description: Optional[str] = None

    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None

 

class TaskResponse(BaseModel):

    id: int

    title: str

    description: Optional[str]

    status: TaskStatus

    created_by: int

    assigned_to: Optional[int]
    completion_processed: bool
    created_at: datetime

    updated_at: datetime


    class Config:

        from_attributes = True