"""Optional logging.Handler that forwards records to OpenObserve."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .handler import system_log_to_record

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .client import OpenObserveClient


class ExportingLogHandler(logging.Handler):
    """Forward logging.LogRecord instances to OpenObserve."""

    def __init__(self, hass: HomeAssistant, client: OpenObserveClient) -> None:
        super().__init__()
        self._hass = hass
        self._client = client

    def emit(self, record: logging.LogRecord) -> None:
        event_data: dict[str, Any] = {
            "name": record.name,
            "message": [record.getMessage()],
            "level": record.levelname,
            "source": (record.pathname, record.lineno),
            "timestamp": record.created,
        }
        if record.exc_info and record.exc_info[1]:
            import traceback

            event_data["exception"] = "".join(
                traceback.format_exception(*record.exc_info)
            )
        o2_record = system_log_to_record(event_data)
        self._hass.loop.call_soon_threadsafe(
            self._client.enqueue_log, o2_record
        )
