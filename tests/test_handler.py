"""Unit tests for record builders (no HA runtime required)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components"))

from openobserve.handler import (  # noqa: E402
    entity_matches_exclude,
    redact_secrets,
    system_log_to_record,
)


def test_redact_secrets() -> None:
    data = {"password": "secret", "entity_id": "light.kitchen"}
    result = redact_secrets(data)
    assert result["password"] == "[REDACTED]"
    assert result["entity_id"] == "light.kitchen"


def test_system_log_to_record() -> None:
    record = system_log_to_record(
        {
            "name": "homeassistant",
            "message": ["Test message"],
            "level": "WARNING",
            "source": ("/config/custom.py", 42),
        }
    )
    assert record["level"] == "warning"
    assert record["message"] == "Test message"
    assert record["record_type"] == "log"
    assert record["source_line"] == 42


def test_entity_exclude() -> None:
    assert entity_matches_exclude("sensor.temp", ["sensor.*"])
    assert not entity_matches_exclude("light.kitchen", ["sensor.*"])
