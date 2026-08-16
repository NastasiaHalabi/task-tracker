"""Regression tests for final-project bug and security corrections."""

import pytest


@pytest.mark.parametrize(
    "field",
    ["title", "description", "status", "priority", "tags"],
)
def test_patch_rejects_null_for_non_nullable_fields(client, created_task, field):
    response = client.patch(
        f"/tasks/{created_task['id']}",
        json={field: None},
    )
    assert response.status_code == 422


def test_cors_preflight_rejects_null_origin(client):
    response = client.options(
        "/tasks",
        headers={
            "Origin": "null",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_allows_documented_local_frontend(client):
    origin = "http://localhost:5500"
    response = client.options(
        "/tasks",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
