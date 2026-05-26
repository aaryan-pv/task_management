from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List
 

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


class TaskAssign(BaseModel):

    assigned_to: int

 

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



class BulkTaskCreate(BaseModel):

    tasks: List[TaskCreate]


class BulkTaskStatusItem(BaseModel):

    task_id: int

    status: TaskStatus


class BulkTaskStatusUpdate(BaseModel):

    tasks: List[BulkTaskStatusItem]


class BulkOperationResult(BaseModel):

    success: bool

    task_id: Optional[int] = None

    error: Optional[str] = None


class BulkResponse(BaseModel):

    success_count: int

    failure_count: int

    results: List[BulkOperationResult]
    class Config:

        from_attributes = True