from typing import Optional

from sqlalchemy import asc
from sqlalchemy import desc

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.enums import TaskStatus


class TaskRepository:


    @staticmethod
    def create_task(
        db: Session,
        task_data: dict
    ):

        task = Task(**task_data)

        db.add(task)

        return task


    @staticmethod
    def get_task_by_id(
        db: Session,
        task_id: int
    ):

        return db.query(Task).filter(
            Task.id == task_id
        ).first()


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

        query = db.query(Task)

        # FILTER BY STATUS
        if status:

            query = query.filter(
                Task.status == status
            )

        # FILTER BY ASSIGNED USER
        if assigned_to:

            query = query.filter(
                Task.assigned_to == assigned_to
            )

        # FILTER BY CREATOR
        if created_by:

            query = query.filter(
                Task.created_by == created_by
            )

        # SORTING
        sort_column = getattr(
            Task,
            sort_by,
            Task.created_at
        )

        if order == "asc":

            query = query.order_by(
                asc(sort_column)
            )

        else:

            query = query.order_by(
                desc(sort_column)
            )

        # PAGINATION
        query = query.offset(offset).limit(limit)

        return query.all()


    @staticmethod
    def update_task(
        task,
        update_data: dict
    ):

        for key, value in update_data.items():

            setattr(task, key, value)

        return task


    @staticmethod
    def delete_task(
        db: Session,
        task
    ):

        db.delete(task)