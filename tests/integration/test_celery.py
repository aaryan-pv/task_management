import time

from unittest.mock import patch

from conftest import client

from app.models.task import Task
from app.models.enums import TaskStatus
from app.workers.task_worker import process_task_completion


def _create_task(title="Celery Task"):

    response = client.post(
        "/tasks/",
        json={
            "title": title,
            "description": "Background task",
            "created_by": 1,
            "assigned_to": 1
        }
    )

    assert response.status_code == 200

    return response.json()


@patch("app.services.task_service.process_task_completion.delay")
def test_celery_queued_when_task_marked_completed(mock_delay):
    """Transitioning to completed should enqueue the worker exactly once."""

    task = _create_task("Queue On Complete")
    task_id = task["id"]

    assert client.put(
        f"/tasks/{task_id}",
        json={"status": "in_progress"}
    ).status_code == 200

    assert mock_delay.call_count == 0

    assert client.put(
        f"/tasks/{task_id}",
        json={"status": "completed"}
    ).status_code == 200

    mock_delay.assert_called_once_with(task_id)


@patch(
    "app.services.task_service.process_task_completion.delay",
    side_effect=lambda *_a, **_kw: time.sleep(0)
)
def test_complete_request_is_non_blocking(mock_delay):
    """The HTTP request returns quickly because the worker is enqueued, not run."""

    task = _create_task("Non-Blocking")
    task_id = task["id"]

    client.put(f"/tasks/{task_id}", json={"status": "in_progress"})

    start = time.perf_counter()
    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "completed"}
    )
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.0, f"Request took {elapsed:.2f}s; worker is blocking the API"
    mock_delay.assert_called_once()


def test_celery_retry_configuration():
    """The worker is configured with autoretry + bounded max_retries."""

    assert process_task_completion.autoretry_for == (Exception,)
    assert process_task_completion.retry_backoff is True
    assert process_task_completion.retry_kwargs == {"max_retries": 3}


@patch("app.workers.task_worker.time.sleep")
def test_worker_processes_completion_and_marks_idempotent(
    mock_sleep,
    db_session
):
    """Mock worker runs in-process, marks task completed, and flips idempotency flag."""

    task = Task(
        title="To Process",
        description="x",
        created_by=1,
        assigned_to=1,
        status=TaskStatus.IN_PROGRESS,
        completion_processed=False
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    process_task_completion.apply(args=[task.id])

    updated_task = (
        db_session.query(Task)
        .filter(Task.id == task.id)
        .first()
    )

    assert updated_task.status == TaskStatus.COMPLETED
    assert updated_task.completion_processed is True
