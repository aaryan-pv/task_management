from typing import Optional

from sqlalchemy.orm import Session

from app.core.constants import ALLOWED_STATUS_TRANSITIONS
from app.models.enums import TaskStatus

from app.repositories.task_repository import (
    TaskRepository
)

from app.services.cache_service import (
    CacheService
)

from app.utils.exceptions import (
    BadRequestException,
    NotFoundException
)

from app.utils.logger import logger
from app.workers.task_worker import (
    process_task_completion
)
def validate_status_transition(
    current_status: TaskStatus,
    new_status: TaskStatus
):

    allowed = ALLOWED_STATUS_TRANSITIONS.get(
        current_status,
        []
    )

    return new_status in allowed


class TaskService:

    @staticmethod
    def _serialize_task(task) -> dict:
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "created_by": task.created_by,
            "assigned_to": task.assigned_to,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }

    @staticmethod
    def create_task(
        db: Session,
        payload
    ):

        logger.info(
            f"Creating task created_by={payload.created_by}"
        )

        task = TaskRepository.create_task(
            db=db,
            task_data=payload.model_dump()
        )

        db.commit()
        db.refresh(task)

        CacheService.delete(
            f"tasks:user:{task.created_by}"
        )

        return task

    @staticmethod
    def get_task(
        db: Session,
        task_id: int
    ):

        logger.info(
            f"Fetching task_id={task_id}"
        )

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:
            raise NotFoundException(
                detail="Task not found"
            )

        CacheService.set(
            f"task:{task_id}",
            TaskService._serialize_task(task)
        )

        return task

    @staticmethod
    def get_tasks(
        db: Session,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[int] = None,
        created_by: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "created_at",
        order: str = "desc"
    ):

        logger.info(
            f"""
            Listing tasks
            status={status}
            assigned_to={assigned_to}
            created_by={created_by}
            limit={limit}
            offset={offset}
            """
        )

        tasks = TaskRepository.get_tasks(
            db=db,
            status=status,
            assigned_to=assigned_to,
            created_by=created_by,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )

        if created_by:
            CacheService.set(
                f"tasks:user:{created_by}",
                [
                    TaskService._serialize_task(task)
                    for task in tasks
                ]
            )

        return tasks


    @staticmethod
    def assign_task(
        db: Session,
        task_id: int,
        assigned_to: int
    ):

        logger.info(
            f"Assigning task_id={task_id} to user_id={assigned_to}"
        )

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:
            raise NotFoundException(
                detail="Task not found"
            )

        if task.status != TaskStatus.PENDING:
            raise BadRequestException(
                detail="Only pending tasks can be assigned"
            )

        updated_task = TaskRepository.update_task(
            task,
            {"assigned_to": assigned_to}
        )

        db.commit()
        db.refresh(updated_task)

        CacheService.delete(f"task:{task_id}")
        CacheService.delete(f"tasks:user:{task.created_by}")

        return updated_task

    @staticmethod
    def delete_task(
        db: Session,
        task_id: int
    ):

        logger.info(
            f"Deleting task_id={task_id}"
        )

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:
            raise NotFoundException(
                detail="Task not found"
            )

        created_by = task.created_by

        TaskRepository.delete_task(
            db,
            task
        )

        db.commit()

        CacheService.delete(f"task:{task_id}")
        CacheService.delete(f"tasks:user:{created_by}")

        return {
            "message": "Task deleted successfully"
        }




    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        payload
    ):

        logger.info(
            f"Updating task_id={task_id}"
        )

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:
            raise NotFoundException(
                detail="Task not found"
            )

        update_data = payload.model_dump(
            exclude_unset=True
        )

        if "status" in update_data:
            old_status = task.status
            new_status = update_data["status"]

            allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
                old_status,
                []
            )

            if new_status not in allowed_statuses:
                raise BadRequestException(
                    detail=(
                        f"Invalid status transition: "
                        f"{old_status} -> {new_status}"
                    )
                )

        updated_task = TaskRepository.update_task(
            task,
            update_data
        )

        db.commit()
        if (
    task.status.value.lower() == "completed"):

            logger.info(
                f"Queueing celery task "
                f"for task_id={task.id}"
                )

            process_task_completion.delay(
                task.id
                )
        db.refresh(updated_task)

        CacheService.delete(f"task:{task_id}")
        CacheService.delete(f"tasks:user:{task.created_by}")

        return updated_task
