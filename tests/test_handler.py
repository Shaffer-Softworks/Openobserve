"""Unit tests for pure helpers (no HA runtime required)."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1] / "custom_components"
_PKG = "openobserve"


def _load(name: str, rel: str):
    path = _ROOT / _PKG / rel
    spec = importlib.util.spec_from_file_location(f"{_PKG}.{name}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"{_PKG}.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


def setup_module() -> None:
    pkg = types.ModuleType(_PKG)
    pkg.__path__ = [str(_ROOT / _PKG)]  # type: ignore[attr-defined]
    sys.modules[_PKG] = pkg
    _load("const", "const.py")
    _load("util", "util.py")
    _load("handler", "handler.py")


setup_module()
handler = sys.modules[f"{_PKG}.handler"]
util = sys.modules[f"{_PKG}.util"]


def test_redact_secrets() -> None:
    data = {"password": "secret", "entity_id": "light.kitchen"}
    result = util.redact_secrets(data)
    assert result["password"] == "[REDACTED]"
    assert result["entity_id"] == "light.kitchen"


def test_system_log_to_record() -> None:
    record = handler.system_log_to_record(
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
    assert util.entity_matches_exclude("sensor.temp", ["sensor.*"])
    assert not util.entity_matches_exclude("light.kitchen", ["sensor.*"])
