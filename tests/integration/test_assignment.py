from concurrent.futures import ThreadPoolExecutor

from conftest import client


def _create_pending_task(title="Assign Task"):
    """Create a task in pending status with no assignee."""

    response = client.post(
        "/tasks/",
        json={
            "title": title,
            "description": "Assignment",
            "created_by": 1
        }
    )

    assert response.status_code == 200

    return response.json()


def test_assign_pending_task_succeeds():
    """Assigning an active user to a pending unassigned task works."""

    task = _create_pending_task("Happy Assign")

    response = client.put(
        f"/tasks/{task['id']}/assign",
        json={"assigned_to": 2}
    )

    assert response.status_code == 200
    assert response.json()["assigned_to"] == 2
 

 

def test_concurrent_double_assign_only_one_wins():
    """Two simultaneous assigns on the same pending task: exactly one succeeds."""

    task = _create_pending_task("Concurrent Assign")
    task_id = task["id"]

    def assign(user_id):
        return client.put(
            f"/tasks/{task_id}/assign",
            json={"assigned_to": user_id}
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(assign, 1)
        f2 = executor.submit(assign, 2)
        r1, r2 = f1.result(), f2.result()

    success = sum(r.status_code == 200 for r in (r1, r2))
    failure = sum(r.status_code == 400 for r in (r1, r2))

    assert success == 1, f"Expected exactly one success, got {success}"
    assert failure == 1, f"Expected exactly one 400, got {failure}"

    final = client.get(f"/tasks/{task_id}").json()
    assert final["assigned_to"] in (1, 2)
