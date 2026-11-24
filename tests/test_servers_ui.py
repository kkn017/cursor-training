"""Add/remove servers UI tests."""

import re

from tests.conftest import csrf_from


def _server_id_from_servers_page(html: str) -> str:
    match = re.search(r'/servers/([0-9a-f]+)/remove', html)
    assert match, "expected remove form with server id"
    return match.group(1)


def test_servers_requires_auth(client):
    response = client.get("/servers", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_add_and_remove_server(auth_client):
    token = csrf_from(auth_client)
    add = auth_client.post(
        "/servers",
        data={
            "csrf_token": token,
            "hostname": "demo.local",
            "ssh_user": "ubuntu",
            "ssh_port": "22",
        },
        follow_redirects=True,
    )
    assert add.status_code == 200
    assert b"demo.local" in add.data

    list_page = auth_client.get("/servers")
    assert b"demo.local" in list_page.data
    server_id = _server_id_from_servers_page(list_page.get_data(as_text=True))

    token = csrf_from(auth_client)
    removed = auth_client.post(
        f"/servers/{server_id}/remove",
        data={"csrf_token": token},
        follow_redirects=True,
    )
    assert removed.status_code == 200
    assert b"demo.local" not in removed.data


def test_remove_rejects_get(auth_client):
    response = auth_client.get("/servers/abc/remove", follow_redirects=False)
    assert response.status_code == 405


def test_add_requires_csrf(auth_client):
    response = auth_client.post(
        "/servers",
        data={"hostname": "x.local", "ssh_user": "u", "ssh_port": "22"},
        follow_redirects=False,
    )
    assert response.status_code == 400
