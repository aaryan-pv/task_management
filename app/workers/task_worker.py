import time

from app.core.celery_app import celery_app

from app.core.database import SessionLocal

from app.models.task import Task
from app.models.user import User

from app.models.enums import TaskStatus

from app.utils.logger import logger


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3}
)
def process_task_completion(
    self,
    task_id: int
):

    db = SessionLocal()

    try:

        logger.info(
            f"Celery worker started "
            f"task_id={task_id}"
        )

        # -----------------------------------
        # FETCH TASK
        # -----------------------------------
        task = db.query(Task).filter(
            Task.id == task_id
        ).first()

        if not task:

            logger.error(
                f"Task not found "
                f"task_id={task_id}"
            )

            return

        # -----------------------------------
        # IDEMPOTENCY CHECK
        # -----------------------------------
        if task.completion_processed:

            logger.info(
                f"Task already processed "
                f"task_id={task_id}"
            )

            return

        # -----------------------------------
        # SIMULATE BACKGROUND WORK
        # -----------------------------------
        logger.info(
            f"Processing completion "
            f"task_id={task_id}"
        )

        time.sleep(5)

        # -----------------------------------
        # MARK TASK COMPLETED
        # -----------------------------------
        task.status = TaskStatus.COMPLETED

        task.completion_processed = True

        db.commit()

        db.refresh(task)

        logger.info(
            f"Worker marked task completed "
            f"task_id={task_id}"
        )

    except Exception as e:

        logger.error(
            f"Celery task failed "
            f"task_id={task_id} "
            f"error={str(e)}"
        )

        raise self.retry(exc=e)

    finally:

        db.close()