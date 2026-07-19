"""Tests for due dates / overdue filter and tags features."""

from datetime import timedelta

from app.models import utc_today


def test_create_task_with_valid_due_date_returns_201(client):
    due = (utc_today() + timedelta(days=3)).isoformat()
    response = client.post(
        "/tasks",
        json={"title": "has due date", "due_date": due},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == due
    assert body["is_overdue"] is False


def test_create_task_invalid_due_date_format_returns_422(client):
    response = client.post(
        "/tasks",
        json={"title": "bad date", "due_date": "not-a-date"},
    )
    assert response.status_code == 422


def test_overdue_detection_and_filter(client):
    past = (utc_today() - timedelta(days=2)).isoformat()
    future = (utc_today() + timedelta(days=5)).isoformat()

    overdue_resp = client.post(
        "/tasks",
        json={"title": "overdue task", "due_date": past},
    )
    assert overdue_resp.status_code == 201
    assert overdue_resp.json()["is_overdue"] is True

    on_time = client.post(
        "/tasks",
        json={"title": "future task", "due_date": future},
    )
    assert on_time.status_code == 201
    assert on_time.json()["is_overdue"] is False

    # Done tasks are never overdue even with a past due date
    done_setup = client.post(
        "/tasks",
        json={"title": "done overdue", "due_date": past},
    )
    done_id = done_setup.json()["id"]
    client.patch(f"/tasks/{done_id}", json={"status": "InProgress"})
    done_resp = client.patch(f"/tasks/{done_id}", json={"status": "Done"})
    assert done_resp.status_code == 200
    assert done_resp.json()["is_overdue"] is False

    filtered = client.get("/tasks", params={"overdue": True})
    assert filtered.status_code == 200
    body = filtered.json()
    assert len(body) == 1
    assert body[0]["title"] == "overdue task"
    assert all(task["is_overdue"] for task in body)


def test_update_due_date(client, created_task):
    new_due = (utc_today() + timedelta(days=10)).isoformat()
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={"due_date": new_due},
    )
    assert response.status_code == 200
    assert response.json()["due_date"] == new_due
    assert response.json()["title"] == created_task["title"]


def test_create_task_with_tags_returns_201(client):
    response = client.post(
        "/tasks",
        json={"title": "tagged", "tags": [" backend ", "api"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["tags"] == ["backend", "api"]


def test_create_task_rejects_empty_tag(client):
    response = client.post(
        "/tasks",
        json={"title": "bad tags", "tags": ["ok", "  "]},
    )
    assert response.status_code == 422


def test_update_tags_and_filter_by_tag(client):
    created = client.post(
        "/tasks",
        json={"title": "alpha", "tags": ["urgent", "ops"]},
    ).json()
    client.post("/tasks", json={"title": "beta", "tags": ["ops"]})
    client.post("/tasks", json={"title": "gamma", "tags": ["docs"]})

    updated = client.patch(
        f"/tasks/{created['id']}",
        json={"tags": ["urgent", "frontend"]},
    )
    assert updated.status_code == 200
    assert updated.json()["tags"] == ["urgent", "frontend"]

    by_tag = client.get("/tasks", params={"tag": "ops"})
    assert by_tag.status_code == 200
    titles = {task["title"] for task in by_tag.json()}
    assert titles == {"beta"}

    # Case-insensitive tag filter
    by_case = client.get("/tasks", params={"tag": "URGENT"})
    assert by_case.status_code == 200
    assert len(by_case.json()) == 1
    assert by_case.json()[0]["title"] == "alpha"


def test_preserve_tags_after_unrelated_update(client):
    created = client.post(
        "/tasks",
        json={"title": "keep tags", "tags": ["keep-me"]},
    ).json()
    response = client.patch(
        f"/tasks/{created['id']}",
        json={"description": "only description changed"},
    )
    assert response.status_code == 200
    assert response.json()["tags"] == ["keep-me"]
    assert response.json()["description"] == "only description changed"
