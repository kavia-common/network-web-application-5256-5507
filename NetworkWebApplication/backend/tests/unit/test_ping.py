from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.services.ping import ping_ip


@patch("backend.services.ping.ping")
def test_ping_ip_online(mock_ping):
    # Mock pythonping result object
    mock_result = MagicMock()
    mock_result.success.return_value = True
    mock_result.rtt_avg = 0.012345
    mock_ping.return_value = mock_result

    res = ping_ip("1.2.3.4", timeout_ms=900)
    assert res["status"] == "online"
    assert isinstance(res["latency_ms"], float)
    assert abs(res["latency_ms"] - 12.345) < 0.01
    assert res["timestamp"].endswith("Z")
    mock_ping.assert_called_once()


@patch("backend.services.ping.ping")
def test_ping_ip_offline(mock_ping):
    mock_result = MagicMock()
    mock_result.success.return_value = False
    mock_result.rtt_avg = None
    mock_ping.return_value = mock_result

    res = ping_ip("1.2.3.4", timeout_ms=0)
    assert res["status"] == "offline"
    assert res["latency_ms"] is None
    assert res["timestamp"].endswith("Z")


@patch("backend.services.ping.ping", side_effect=RuntimeError("no perm"))
def test_ping_ip_exception(mock_ping):
    res = ping_ip("1.2.3.4", timeout_ms=1000)
    assert res["status"] == "offline"
    assert res["latency_ms"] is None
    assert res["timestamp"].endswith("Z")
