"""Server detail page tests."""

import re
from unittest.mock import patch

from tests.conftest import csrf_from


def _add_server(auth_client):
    token = csrf_from(auth_client)
    auth_client.post(
        "/servers",
        data={
            "csrf_token": token,
            "hostname": "detail.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
        },
    )
    page = auth_client.get("/servers").get_data(as_text=True)
    match = re.search(r'/servers/([0-9a-f]+)/remove', page)
    assert match
    return match.group(1)


def test_detail_requires_auth(client):
    response = client.get("/servers/abc", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@patch("app.collect_metrics_safe")
def test_detail_renders_mocked_metrics(mock_collect, auth_client):
    server_id = _add_server(auth_client)
    mock_collect.return_value = {
        "reachable": True,
        "error": None,
        "cpu_percent": 8.0,
        "memory": {
            "used_percent": 50.0,
            "used_bytes": 512 * 1048576,
            "free_bytes": 512 * 1048576,
            "total_bytes": 1024 * 1048576,
        },
        "network": {"rx_bytes": 10 * 1048576, "tx_bytes": 20 * 1048576},
        "ports": [{"protocol": "tcp", "port": "22", "local_address": "0.0.0.0:22"}],
    }
    response = auth_client.get(f"/servers/{server_id}")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "detail.local" in html
    assert "8.0%" in html
    assert "Listening ports" in html
    assert ">22<" in html
    assert "content=\"5\"" in html or "5000" in html
    assert "ubuntu" in html
    # Credentials beyond hostname/user/port should not appear
    assert "SSH_PASSWORD" not in html
    assert "BEGIN RSA" not in html
    mock_collect.assert_called_once()
