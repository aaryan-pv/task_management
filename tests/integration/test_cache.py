import logging

from conftest import client, fake_redis_client


def _create_task(title="Cache Task"):

    response = client.post(
        "/tasks/",
        json={
            "title": title,
            "description": "Cache testing",
            "created_by": 1,
            "assigned_to": 1
        }
    )

    assert response.status_code == 200

    return response.json()


def test_cache_populated_with_ttl_on_get_task():
    """GET /tasks/{id} should populate Redis with the configured TTL."""

    task = _create_task("TTL Task")
    task_id = task["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    cached_raw = fake_redis_client.get(f"task:{task_id}")
    assert cached_raw is not None, "task:{id} key should be set after GET"

    ttl = fake_redis_client.ttl(f"task:{task_id}")
    assert 0 < ttl <= 300, f"Expected TTL within (0, 300], got {ttl}"


def test_cache_miss_then_populate_on_first_read():
    """First read after creation has no key; the read populates the cache."""

    task = _create_task("Miss First")
    task_id = task["id"]

    assert fake_redis_client.get(f"task:{task_id}") is None

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

    assert fake_redis_client.get(f"task:{task_id}") is not None


def test_cache_invalidated_on_update():
    """Updating a task evicts both the per-task key and the user-list key."""

    task = _create_task("Invalidate-Update")
    task_id = task["id"]
    created_by = task["created_by"]

    client.get(f"/tasks/{task_id}")
    client.get(f"/tasks/?created_by={created_by}")

    assert fake_redis_client.get(f"task:{task_id}") is not None
    assert fake_redis_client.get(f"tasks:user:{created_by}") is not None

    update_response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated"}
    )
    assert update_response.status_code == 200

    assert fake_redis_client.get(f"task:{task_id}") is None
    assert fake_redis_client.get(f"tasks:user:{created_by}") is None


def test_cache_invalidated_on_delete():
    """Deleting a task evicts the cached entries for that task and its owner."""

    task = _create_task("Invalidate-Delete")
    task_id = task["id"]
    created_by = task["created_by"]

    client.get(f"/tasks/{task_id}")
    client.get(f"/tasks/?created_by={created_by}")

    assert fake_redis_client.get(f"task:{task_id}") is not None

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    assert fake_redis_client.get(f"task:{task_id}") is None
    assert fake_redis_client.get(f"tasks:user:{created_by}") is None


def test_cache_redis_down_falls_back_to_db_and_logs(monkeypatch, caplog):
    """If Redis raises, the request still succeeds against the DB and logs the error."""

    task = _create_task("Redis-Down")
    task_id = task["id"]

    def boom(*_args, **_kwargs):
        raise ConnectionError("redis is down")

    monkeypatch.setattr(fake_redis_client, "setex", boom)
    monkeypatch.setattr(fake_redis_client, "get", boom)
    monkeypatch.setattr(fake_redis_client, "delete", boom)

    with caplog.at_level(logging.ERROR, logger="task_management"):
        response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["id"] == task_id

    assert any(
        "Redis" in record.message for record in caplog.records
    ), "Expected a Redis-related ERROR log"
