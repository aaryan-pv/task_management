from sqlalchemy.orm import Session

from app.repositories.task_repository import (
    TaskRepository
)

from app.repositories.user_repository import (
    UserRepository
)

from app.utils.exceptions import (
    NotFoundException,
    BadRequestException
)

from app.utils.logger import logger

from app.models.enums import TaskStatus

from app.core.constants import (
    ALLOWED_STATUS_TRANSITIONS
)


class TaskService:


    @staticmethod
    def create_task(
        db: Session,
        payload
    ):

        creator = UserRepository.get_user_by_id(
            db,
            payload.created_by
        )

        if not creator:

            raise NotFoundException(
                detail="Creator user not found"
            )

        task = TaskRepository.create_task(
            db,
            payload.model_dump()
        )

        db.commit()

        db.refresh(task)

        logger.info(
            f"Task created task_id={task.id}"
        )

        return task


    @staticmethod
    def get_task(
        db: Session,
        task_id: int
    ):

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:

            raise NotFoundException(
                detail="Task not found"
            )

        return task


    @staticmethod
    def get_tasks(
        db: Session,
        status=None,
        assigned_to=None,
        limit=10,
        offset=0,
        sort_by="created_at",
        order="desc"
    ):

        logger.info(
            f"""
            Listing tasks
            status={status}
            assigned_to={assigned_to}
            limit={limit}
            offset={offset}
            """
        )

        return TaskRepository.get_tasks(
            db=db,
            status=status,
            assigned_to=assigned_to,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )


    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        payload
    ):

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

        # STATE MACHINE VALIDATION
        if "status" in update_data:

            old_status = task.status

            new_status = update_data["status"]

            allowed = ALLOWED_STATUS_TRANSITIONS[
                old_status
            ]

            if new_status not in allowed:

                raise BadRequestException(
                    detail=(
                        f"Invalid transition "
                        f"{old_status} -> {new_status}"
                    )
                )

            logger.info(
                f"""
                Status transition
                task_id={task.id}
                old_status={old_status}
                new_status={new_status}
                """
            )

        updated_task = TaskRepository.update_task(
            task,
            update_data
        )

        db.commit()

        db.refresh(updated_task)

        return updated_task


    @staticmethod
    def delete_task(
        db: Session,
        task_id: int
    ):

        task = TaskRepository.get_task_by_id(
            db,
            task_id
        )

        if not task:

            raise NotFoundException(
                detail="Task not found"
            )

        TaskRepository.delete_task(
            db,
            task
        )

        db.commit()

        return {
            "message": "Task deleted successfully"
        }


    @staticmethod
    def assign_task(
        db: Session,
        task_id: int,
        assigned_to: int
    ):

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
                detail=(
                    "Only pending tasks "
                    "can be assigned"
                )
            )

        user = UserRepository.get_user_by_id(
            db,
            assigned_to
        )

        if not user:

            raise NotFoundException(
                detail="Assigned user not found"
            )

        if not user.is_active:

            raise BadRequestException(
                detail="User is inactive"
            )

        if task.assigned_to:

            raise BadRequestException(
                detail="Task already assigned"
            )

        task.assigned_to = assigned_to

        db.commit()

        db.refresh(task)

        logger.info(
            f"""
            Task assigned
            task_id={task.id}
            assigned_to={assigned_to}
            """
        )

        return task