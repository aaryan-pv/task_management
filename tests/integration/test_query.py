from unittest.mock import patch

from conftest import client


def _create_task(
    title="Query Task",
    created_by=1,
    assigned_to=None,
    status=None
):

    payload = {
        "title": title,
        "description": "Query",
        "created_by": created_by
    }

    if assigned_to is not None:
        payload["assigned_to"] = assigned_to

    if status is not None:
        payload["status"] = status

    response = client.post("/tasks/", json=payload)
    assert response.status_code == 200

    return response.json()


def _seed_dataset():
    """Mix of statuses, owners, and assignees for filter/sort/paginate tests."""

    t1 = _create_task("alpha", created_by=1, assigned_to=1)
    t2 = _create_task("beta", created_by=1)
    t3 = _create_task("gamma", created_by=2, assigned_to=2)
    t4 = _create_task("delta", created_by=2)

    client.put(f"/tasks/{t2['id']}", json={"status": "in_progress"})

    with patch(
        "app.services.task_service.process_task_completion.delay"
    ):
        client.put(f"/tasks/{t3['id']}", json={"status": "in_progress"})
        client.put(f"/tasks/{t3['id']}", json={"status": "completed"})

    return {"t1": t1, "t2": t2, "t3": t3, "t4": t4}


def test_filters_by_status_assignee_and_creator():
    """Filtering should narrow results by status, assigned_to and created_by."""

    _seed_dataset()

    pending = client.get("/tasks/?status=pending&limit=100").json()
    assert pending and all(t["status"] == "pending" for t in pending)

    assigned = client.get("/tasks/?assigned_to=1&limit=100").json()
    assert all(t["assigned_to"] == 1 for t in assigned)

    owned = client.get("/tasks/?created_by=2&limit=100").json()
    assert owned and all(t["created_by"] == 2 for t in owned)


def test_pagination_limit_and_offset():
    """limit/offset return disjoint pages."""

    _seed_dataset()

    page1 = client.get("/tasks/?limit=2&offset=0").json()
    page2 = client.get("/tasks/?limit=2&offset=2").json()

    assert len(page1) == 2
    assert len(page2) >= 1

    assert {t["id"] for t in page1}.isdisjoint({t["id"] for t in page2})


def test_sort_by_id_ascending_and_descending():
    """sort_by + order produces a deterministically ordered list."""

    _seed_dataset()

    asc_ids = [t["id"] for t in client.get("/tasks/?sort_by=id&order=asc&limit=100").json()]
    desc_ids = [t["id"] for t in client.get("/tasks/?sort_by=id&order=desc&limit=100").json()]

    assert asc_ids == sorted(asc_ids)
    assert desc_ids == sorted(desc_ids, reverse=True)


def test_invalid_query_params_return_422():
    """Bad enum values and bad pagination types are rejected at the boundary."""

    assert client.get("/tasks/?status=garbage").status_code == 422
    assert client.get("/tasks/?limit=not-a-number").status_code == 422
