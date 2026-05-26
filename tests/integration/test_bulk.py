from unittest.mock import patch

from conftest import client


def test_bulk_create_returns_ids_for_all_items():
    """Every item in a successful bulk create should come back with a real DB id."""

    response = client.post(
        "/tasks/bulk",
        json={
            "tasks": [
                {
                    "title": "Bulk 1",
                    "description": "Task 1",
                    "created_by": 1,
                    "assigned_to": 1
                },
                {
                    "title": "Bulk 2",
                    "description": "Task 2",
                    "created_by": 1,
                    "assigned_to": 1
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success_count"] == 2
    assert data["failure_count"] == 0
    assert len(data["results"]) == 2
    assert all(r["success"] is True for r in data["results"])
    assert all(isinstance(r["task_id"], int) for r in data["results"])


def test_bulk_create_partial_failure_does_not_block_valid_items():
    """A bad item (FK violation) must fail individually without losing the good ones."""

    response = client.post(
        "/tasks/bulk",
        json={
            "tasks": [
                {"title": "Good A", "created_by": 1},
                {"title": "Bad", "created_by": 99999},
                {"title": "Good B", "created_by": 1}
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success_count"] == 2
    assert data["failure_count"] == 1

    failures = [r for r in data["results"] if not r["success"]]
    assert len(failures) == 1
    assert failures[0]["error"]


def test_bulk_create_validation_error_for_missing_required_field():
    """Missing required schema fields are rejected at the API boundary."""

    response = client.post(
        "/tasks/bulk",
        json={
            "tasks": [
                {"description": "no title", "created_by": 1}
            ]
        }
    )

    assert response.status_code == 422


@patch("app.services.task_service.process_task_completion.delay")
def test_bulk_status_update_applies_valid_transitions(mock_delay):
    """Bulk status update should commit valid transitions and report task ids."""

    create_response = client.post(
        "/tasks/bulk",
        json={
            "tasks": [
                {"title": "S1", "created_by": 1},
                {"title": "S2", "created_by": 1}
            ]
        }
    )

    ids = [r["task_id"] for r in create_response.json()["results"]]

    response = client.put(
        "/tasks/bulk/status",
        json={
            "tasks": [
                {"task_id": ids[0], "status": "in_progress"},
                {"task_id": ids[1], "status": "in_progress"}
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["success_count"] == 2
    assert data["failure_count"] == 0
    assert {r["task_id"] for r in data["results"]} == set(ids)

    for tid in ids:
        assert client.get(f"/tasks/{tid}").json()["status"] == "in_progress"

    mock_delay.assert_not_called()


# @patch("app.services.task_service.process_task_completion.delay")
# def test_bulk_status_update_partial_failure(mock_delay):
#     """Mix of valid and invalid transitions reports each item independently."""

#     create_response = client.post(
#         "/tasks/bulk",
#         json={
#             "tasks": [
#                 {"title": "Mixed-ok", "created_by": 1},
#                 {"title": "Mixed-bad", "created_by": 1}
#             ]
#         }
#     )
#     good_id, bad_id = [r["task_id"] for r in create_response.json()["results"]]

#     response = client.put(
#         "/tasks/bulk/status",
#         json={
#             "tasks": [
#                 {"task_id": good_id, "status": "in_progress"},
#                 {"task_id": bad_id, "status": "completed"},
#                 {"task_id": 99999, "status": "in_progress"}
#             ]
#         }
#     )

#     assert response.status_code == 200

#     data = response.json()
#     assert data["success_count"] == 1
#     assert data["failure_count"] == 2

#     by_id = {
#         r.get("task_id"): r
#         for r in data["results"]
#         if r.get("task_id") is not None
#     }
#     assert by_id[good_id]["success"] is True
#     assert by_id[bad_id]["success"] is False
#     assert "Invalid status transition" in by_id[bad_id]["error"]

#     assert client.get(f"/tasks/{good_id}").json()["status"] == "in_progress"
#     assert client.get(f"/tasks/{bad_id}").json()["status"] == "pending"

#     mock_delay.assert_not_called()
