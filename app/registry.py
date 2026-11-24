"""Local JSON registry for monitored Linux servers."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

HOST_RE = re.compile(
    r"^(?:(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?|"
    r"(?:\d{1,3}\.){3}\d{1,3}|localhost)$"
)
USER_RE = re.compile(r"^[a-zA-Z0-9._-]{1,64}$")


class RegistryError(ValueError):
    """Invalid server data or unknown id."""


def default_data_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    return root / "data" / "servers.json"


class ServerRegistry:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_data_path()

    def _read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        servers = payload.get("servers", [])
        if not isinstance(servers, list):
            return []
        return servers

    def _write(self, servers: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump({"servers": servers}, fh, indent=2)
            fh.write("\n")
        tmp.replace(self.path)

    def list_servers(self) -> list[dict[str, Any]]:
        return list(self._read())

    def get(self, server_id: str) -> dict[str, Any] | None:
        for server in self._read():
            if server.get("id") == server_id:
                return server
        return None

    @staticmethod
    def validate(hostname: str, ssh_user: str, ssh_port: int | str) -> tuple[str, str, int]:
        host = (hostname or "").strip()
        user = (ssh_user or "").strip()
        if not host or not HOST_RE.match(host):
            raise RegistryError("Invalid hostname or IP.")
        if not user or not USER_RE.match(user):
            raise RegistryError("Invalid SSH user.")
        try:
            port = int(ssh_port)
        except (TypeError, ValueError) as exc:
            raise RegistryError("SSH port must be an integer.") from exc
        if port < 1 or port > 65535:
            raise RegistryError("SSH port must be between 1 and 65535.")
        return host, user, port

    def add(self, hostname: str, ssh_user: str, ssh_port: int | str = 22) -> dict[str, Any]:
        host, user, port = self.validate(hostname, ssh_user, ssh_port)
        servers = self._read()
        server = {
            "id": uuid.uuid4().hex,
            "hostname": host,
            "ssh_user": user,
            "ssh_port": port,
        }
        servers.append(server)
        self._write(servers)
        return server

    def remove(self, server_id: str) -> bool:
        servers = self._read()
        remaining = [s for s in servers if s.get("id") != server_id]
        if len(remaining) == len(servers):
            return False
        self._write(remaining)
        return True
