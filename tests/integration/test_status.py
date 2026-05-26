from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from conftest import client


def _create_task(title="Status Task"):

    response = client.post(
        "/tasks/",
        json={
            "title": title,
            "description": "Status flow",
            "created_by": 1,
            "assigned_to": 1
        }
    )

    assert response.status_code == 200

    return response.json()


def test_valid_pending_to_in_progress():
    """pending -> in_progress is an allowed transition."""

    task = _create_task("Valid Transition")

    response = client.put(
        f"/tasks/{task['id']}",
        json={"status": "in_progress"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_reject_terminal_state():
    """Once completed, no further transitions are allowed."""

    task = _create_task("Terminal Completed")
    task_id = task["id"]

    assert client.put(
        f"/tasks/{task_id}",
        json={"status": "in_progress"}
    ).status_code == 200

    with patch(
        "app.services.task_service.process_task_completion.delay"
    ):
        assert client.put(
            f"/tasks/{task_id}",
            json={"status": "completed"}
        ).status_code == 200

    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "in_progress"}
    )

    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["detail"]


def test_invalid_status_value_returns_422():
    """Pydantic should reject statuses outside the enum."""

    task = _create_task("Invalid Enum")

    response = client.put(
        f"/tasks/{task['id']}",
        json={"status": "not-a-real-status"}
    )

    assert response.status_code == 422


def test_concurrent_status_updates_keep_state_valid():
    """Concurrent updates should never leave the row in an invalid state."""

    task = _create_task("Concurrent Status")
    task_id = task["id"]

    def update(status_value):
        return client.put(
            f"/tasks/{task_id}",
            json={"status": status_value}
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(update, "in_progress")
        f2 = executor.submit(update, "cancelled")
        r1, r2 = f1.result(), f2.result()

    assert {r1.status_code, r2.status_code}.issubset({200, 400})

    final = client.get(f"/tasks/{task_id}").json()
    assert final["status"] in {"in_progress", "cancelled", "pending"}
