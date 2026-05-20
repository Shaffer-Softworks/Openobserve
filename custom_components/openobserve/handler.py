"""Build OpenObserve JSON records from HA logs and events."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .util import entity_matches_exclude, redact_secrets

if TYPE_CHECKING:
    from homeassistant.core import Event, State

SERVICE_NAME = "home-assistant"
APP_NAME = "core"


def _iso_timestamp(dt: datetime | None = None) -> str:
    if dt is None:
        dt = datetime.now(tz=UTC)
    elif dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _state_summary(state: "State | None") -> str | None:
    if state is None:
        return None
    return f"{state.state}"


def system_log_to_record(event_data: dict[str, Any]) -> dict[str, Any]:
    """Convert a system_log_event payload to an OpenObserve record."""
    messages = event_data.get("message", [])
    message = "\n".join(messages) if isinstance(messages, list) else str(messages)
    level = str(event_data.get("level", "INFO")).lower()
    source = event_data.get("source")
    source_path: str | None = None
    source_line: int | None = None
    if source and isinstance(source, (tuple, list)) and len(source) >= 2:
        source_path = str(source[0])
        source_line = int(source[1])

    record: dict[str, Any] = {
        "@timestamp": _iso_timestamp(),
        "service": SERVICE_NAME,
        "app": APP_NAME,
        "record_type": "log",
        "level": level,
        "message": message,
        "logger": event_data.get("name"),
    }
    if source_path:
        record["source_path"] = source_path
    if source_line is not None:
        record["source_line"] = source_line
    if event_data.get("exception"):
        record["exception"] = event_data["exception"]
    if event_data.get("count"):
        record["count"] = event_data["count"]
    return record


def ha_event_to_record(
    event: "Event",
    *,
    state_only: bool = True,
    include_body: bool = False,
) -> dict[str, Any]:
    """Convert a HA bus event to an OpenObserve record."""
    data = event.data or {}
    event_type = event.event_type
    level = "info"
    message = event_type
    entity_id: str | None = None

    if event_type == "state_changed":
        entity_id = data.get("entity_id")
        old_state = data.get("old_state")
        new_state = data.get("new_state")
        old_summary = _state_summary(old_state)
        new_summary = _state_summary(new_state)
        message = f"{entity_id} changed from {old_summary} to {new_summary}"
    elif event_type == "call_service":
        domain = data.get("domain")
        service = data.get("service")
        message = f"{domain}.{service}"
    else:
        message = event_type

    record: dict[str, Any] = {
        "@timestamp": _iso_timestamp(event.time_fired),
        "service": SERVICE_NAME,
        "app": APP_NAME,
        "record_type": "event",
        "event_type": event_type,
        "level": level,
        "message": message,
    }

    if entity_id:
        record["entity_id"] = entity_id

    if event_type == "state_changed":
        old_state = data.get("old_state")
        new_state = data.get("new_state")
        if state_only:
            if old_state is not None:
                record["old_state"] = old_state.state
            if new_state is not None:
                record["new_state"] = new_state.state
        else:
            if old_state is not None:
                record["old_state"] = old_state.as_dict()
            if new_state is not None:
                record["new_state"] = new_state.as_dict()
    elif event_type == "call_service":
        record["domain"] = data.get("domain")
        record["service"] = data.get("service")
        service_data = redact_secrets(data.get("service_data") or {})
        if service_data:
            record["service_data"] = json.dumps(service_data)
    elif include_body:
        record["event_data"] = json.dumps(redact_secrets(dict(data)))

    return record
