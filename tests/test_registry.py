"""Server registry unit tests."""

import pytest

from app.registry import RegistryError, ServerRegistry


def test_add_list_remove(tmp_path):
    reg = ServerRegistry(tmp_path / "servers.json")
    assert reg.list_servers() == []
    server = reg.add("host.example", "ubuntu", 22)
    assert server["hostname"] == "host.example"
    assert server["ssh_user"] == "ubuntu"
    assert server["ssh_port"] == 22
    assert "id" in server
    listed = reg.list_servers()
    assert len(listed) == 1
    assert reg.get(server["id"])["hostname"] == "host.example"
    assert reg.remove(server["id"]) is True
    assert reg.list_servers() == []
    assert reg.remove(server["id"]) is False


@pytest.mark.parametrize(
    "hostname,user,port",
    [
        ("", "ubuntu", 22),
        ("bad host!", "ubuntu", 22),
        ("host.example", "", 22),
        ("host.example", "bad user", 22),
        ("host.example", "ubuntu", 0),
        ("host.example", "ubuntu", 70000),
        ("host.example", "ubuntu", "x"),
    ],
)
def test_validation_rejects_bad_input(tmp_path, hostname, user, port):
    reg = ServerRegistry(tmp_path / "servers.json")
    with pytest.raises(RegistryError):
        reg.add(hostname, user, port)


def test_accepts_ip_and_localhost(tmp_path):
    reg = ServerRegistry(tmp_path / "servers.json")
    a = reg.add("127.0.0.1", "root", 2222)
    b = reg.add("localhost", "admin", 22)
    assert a["ssh_port"] == 2222
    assert b["hostname"] == "localhost"
