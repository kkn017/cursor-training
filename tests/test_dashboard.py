"""Dashboard overview tests."""

from unittest.mock import patch

from tests.conftest import csrf_from


def test_dashboard_requires_auth(client):
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@patch("app.collect_metrics_safe")
def test_dashboard_renders_mocked_metrics(mock_collect, auth_client):
    token = csrf_from(auth_client)
    auth_client.post(
        "/servers",
        data={
            "csrf_token": token,
            "hostname": "box.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
        },
    )
    mock_collect.return_value = {
        "reachable": True,
        "error": None,
        "cpu_percent": 12.5,
        "memory": {"used_percent": 33.0, "used_bytes": 1, "free_bytes": 2, "total_bytes": 3},
        "network": None,
        "ports": [],
    }
    response = auth_client.get("/dashboard")
    assert response.status_code == 200
    assert b"box.local" in response.data
    assert b"Reachable" in response.data
    assert b"12.5%" in response.data
    assert b"33.0%" in response.data
    mock_collect.assert_called()


@patch("app.collect_metrics_safe")
def test_dashboard_shows_unreachable(mock_collect, auth_client):
    token = csrf_from(auth_client)
    auth_client.post(
        "/servers",
        data={
            "csrf_token": token,
            "hostname": "down.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
        },
    )
    mock_collect.return_value = {
        "reachable": False,
        "error": "SSH connection failed: timeout",
        "cpu_percent": None,
        "memory": None,
        "network": None,
        "ports": [],
    }
    response = auth_client.get("/dashboard")
    assert b"Unreachable" in response.data
    assert b"SSH connection failed" in response.data
