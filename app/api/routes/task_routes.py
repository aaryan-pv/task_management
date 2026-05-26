from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.enums import TaskStatus
from app.utils.logger import logger
from app.schemas.task_schema import (
    TaskCreate,
    TaskUpdate,
    TaskAssign,
    TaskResponse,
    BulkTaskCreate,
    BulkTaskStatusUpdate,
    BulkResponse,
)

from app.services.task_service import (
    TaskService
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


# CREATE TASK
@router.post(
    "/",
    response_model=TaskResponse
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db)
):

    return TaskService.create_task(
        db,
        payload
    )

@router.get(
    "/",
    response_model=List[TaskResponse]
)
def get_tasks(
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[int] = None,
    created_by: Optional[int] = None,
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "created_at",
    order: str = "desc",
    db: Session = Depends(get_db)
):

    return TaskService.get_tasks(
        db=db,
        status=status,
        assigned_to=assigned_to,
        created_by=created_by,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    logger.info(
        f"GET /tasks/{task_id} endpoint hit"
    )
    return TaskService.get_task(
        db,
        task_id
    )

# UPDATE TASK
@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db)
):

    return TaskService.update_task(
        db,
        task_id,
        payload
    )


 
# DELETE TASK
@router.delete(
    "/{task_id}"
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    return TaskService.delete_task(
        db,
        task_id
    )


# ASSIGN TASK
@router.put(
    "/{task_id}/assign",
    response_model=TaskResponse
)
def assign_task(
    task_id: int,
    payload: TaskAssign,
    db: Session = Depends(get_db)
):

    return TaskService.assign_task(
        db,
        task_id,
        payload.assigned_to
    )


@router.post(
    "/bulk",
    response_model=BulkResponse
)
def create_tasks_bulk(
    payload: BulkTaskCreate,
    db: Session = Depends(get_db)
):

    return TaskService.create_tasks_bulk(
        db,
        payload
    )


@router.put(
    "/bulk/status",
    response_model=BulkResponse
)
def update_tasks_bulk_status(
    payload: BulkTaskStatusUpdate,
    db: Session = Depends(get_db)
):

    return TaskService.update_tasks_bulk_status(
        db,
        payload
    )