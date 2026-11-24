"""SSH metrics collection tests with mocked Paramiko."""

from unittest.mock import MagicMock, patch

import pytest

from app.metrics import MetricsError, collect_metrics, collect_metrics_safe


def _channel(exit_status=0, out=b"", err=b""):
    stdout = MagicMock()
    stdout.channel.recv_exit_status.return_value = exit_status
    stdout.read.return_value = out
    stderr = MagicMock()
    stderr.read.return_value = err
    return MagicMock(), stdout, stderr


CPU_OUT = b"cpu  100 0 100 800 0 0 0 0 0 0\n"
MEM_OUT = b"              total        used        free\nMem:     1000000000   400000000   600000000\n"
NET_OUT = (
    b"Inter-|   Receive                                                Transmit\n"
    b" face |bytes    packets errs drop fifo frame compressed multicast|bytes\n"
    b"    lo: 100 0 0 0 0 0 0 0 100 0 0 0 0 0 0 0\n"
    b"  eth0: 1000 0 0 0 0 0 0 0 2000 0 0 0 0 0 0 0\n"
)
PORTS_OUT = b"tcp LISTEN 0 128 0.0.0.0:22 0.0.0.0:*\n"


@patch("app.metrics.paramiko.SSHClient")
def test_collect_metrics_success(mock_client_cls):
    client = mock_client_cls.return_value
    client.exec_command.side_effect = [
        _channel(out=CPU_OUT),
        _channel(out=MEM_OUT),
        _channel(out=NET_OUT),
        _channel(out=PORTS_OUT),
    ]
    result = collect_metrics("host", "user", 22)
    assert result["reachable"] is True
    assert result["cpu_percent"] == 20.0
    assert result["memory"]["used_percent"] == 40.0
    assert result["network"]["rx_bytes"] == 1000
    assert result["network"]["tx_bytes"] == 2000
    assert any(p["port"] == "22" for p in result["ports"])
    client.connect.assert_called_once()
    client.close.assert_called_once()


@patch("app.metrics.paramiko.SSHClient")
def test_collect_metrics_connection_failure(mock_client_cls):
    client = mock_client_cls.return_value
    client.connect.side_effect = OSError("refused")
    with pytest.raises(MetricsError, match="SSH connection failed"):
        collect_metrics("host", "user", 22)
    safe = collect_metrics_safe("host", "user", 22)
    assert safe["reachable"] is False
    assert "SSH connection failed" in safe["error"]


@patch("app.metrics.paramiko.SSHClient")
def test_localhost_skips_ssh(mock_client_cls):
    with patch("app.metrics._run_local") as run_local:
        run_local.side_effect = [
            CPU_OUT.decode(),
            MEM_OUT.decode(),
            NET_OUT.decode(),
            PORTS_OUT.decode(),
        ]
        result = collect_metrics("localhost", "monitoring", 22)
    assert result["reachable"] is True
    assert result["cpu_percent"] == 20.0
    mock_client_cls.assert_not_called()


def test_localhost_live_collection():
    result = collect_metrics_safe("localhost", "monitoring", 22)
    assert result["reachable"] is True
    assert result["error"] is None
    assert result["cpu_percent"] is not None
    assert result["memory"] is not None

