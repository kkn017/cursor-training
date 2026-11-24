"""Collect Linux metrics over SSH (or locally for localhost)."""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any

import paramiko

SSH_TIMEOUT = 8
CMD_TIMEOUT = 8

# Fixed commands only — never built from user input.
CMD_CPU = "grep 'cpu ' /proc/stat"
CMD_MEM = "free -b"
CMD_NET = "cat /proc/net/dev"
CMD_PORTS = "ss -lntuH"

LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})


class MetricsError(Exception):
    """SSH or parse failure while collecting metrics."""


def _is_local_host(hostname: str) -> bool:
    return hostname.strip().lower() in LOCAL_HOSTS


def _connect(hostname: str, ssh_user: str, ssh_port: int) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_filename = os.environ.get("SSH_KEY_PATH") or None
    password = os.environ.get("SSH_PASSWORD") or None
    try:
        client.connect(
            hostname=hostname,
            port=ssh_port,
            username=ssh_user,
            key_filename=key_filename,
            password=password,
            timeout=SSH_TIMEOUT,
            allow_agent=True,
            look_for_keys=True,
        )
    except Exception as exc:  # noqa: BLE001 — surface as MetricsError
        client.close()
        raise MetricsError(f"SSH connection failed: {exc}") from exc
    return client


def _run_ssh(client: paramiko.SSHClient, command: str) -> str:
    _stdin, stdout, stderr = client.exec_command(command, timeout=CMD_TIMEOUT)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if exit_status != 0:
        raise MetricsError(err or f"Command failed with exit {exit_status}")
    return out


def _run_local(command: str) -> str:
    """Run a fixed shell command on this machine (localhost demo path)."""
    try:
        completed = subprocess.run(
            ["/bin/sh", "-c", command],
            capture_output=True,
            text=True,
            timeout=CMD_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MetricsError("Local command timed out.") from exc
    if completed.returncode != 0:
        err = (completed.stderr or "").strip()
        raise MetricsError(err or f"Local command failed with exit {completed.returncode}")
    return completed.stdout


def _parse_cpu(raw: str) -> float:
    # /proc/stat: cpu user nice system idle iowait irq softirq ...
    line = raw.strip().splitlines()[0]
    parts = line.split()
    if len(parts) < 5 or parts[0] != "cpu":
        raise MetricsError("Unexpected /proc/stat output.")
    values = [int(x) for x in parts[1:]]
    idle = values[3] + (values[4] if len(values) > 4 else 0)
    total = sum(values)
    if total <= 0:
        return 0.0
    return round(100.0 * (1.0 - idle / total), 1)


def _parse_memory(raw: str) -> dict[str, Any]:
    # free -b: Mem: total used free shared buff/cache available
    for line in raw.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            total = int(parts[1])
            used = int(parts[2])
            free = int(parts[3])
            pct = round(100.0 * used / total, 1) if total else 0.0
            return {
                "total_bytes": total,
                "used_bytes": used,
                "free_bytes": free,
                "used_percent": pct,
            }
    raise MetricsError("Unexpected free output.")


def _parse_network(raw: str) -> dict[str, int]:
    rx = tx = 0
    for line in raw.splitlines():
        if ":" not in line:
            continue
        name, rest = line.split(":", 1)
        iface = name.strip()
        if iface == "lo":
            continue
        cols = rest.split()
        if len(cols) < 9:
            continue
        rx += int(cols[0])
        tx += int(cols[8])
    return {"rx_bytes": rx, "tx_bytes": tx}


def _parse_ports(raw: str) -> list[dict[str, str]]:
    ports: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        proto = parts[0]
        local = parts[4]
        match = re.search(r":(\d+)$", local)
        if not match:
            continue
        port = match.group(1)
        key = f"{proto}:{port}:{local}"
        if key in seen:
            continue
        seen.add(key)
        ports.append({"protocol": proto, "local_address": local, "port": port})
    return ports


def _build_metrics(runner) -> dict[str, Any]:
    cpu_pct = _parse_cpu(runner(CMD_CPU))
    memory = _parse_memory(runner(CMD_MEM))
    network = _parse_network(runner(CMD_NET))
    ports = _parse_ports(runner(CMD_PORTS))
    return {
        "reachable": True,
        "error": None,
        "cpu_percent": cpu_pct,
        "memory": memory,
        "network": network,
        "ports": ports,
    }


def collect_metrics(hostname: str, ssh_user: str, ssh_port: int) -> dict[str, Any]:
    """Return metrics dict or raise MetricsError. Never logs secrets.

    localhost / 127.0.0.1 / ::1 are collected on this machine (no SSH),
    so the demo works without keys when monitoring the app host.
    """
    if _is_local_host(hostname):
        return _build_metrics(_run_local)

    client = _connect(hostname, ssh_user, ssh_port)
    try:
        return _build_metrics(lambda cmd: _run_ssh(client, cmd))
    finally:
        client.close()


def collect_metrics_safe(hostname: str, ssh_user: str, ssh_port: int) -> dict[str, Any]:
    try:
        return collect_metrics(hostname, ssh_user, ssh_port)
    except MetricsError as exc:
        return {
            "reachable": False,
            "error": str(exc),
            "cpu_percent": None,
            "memory": None,
            "network": None,
            "ports": [],
        }
