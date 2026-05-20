"""OpenObserve HTTP ingest client."""

from __future__ import annotations

import asyncio
import base64
import logging
from typing import Any

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_BASE_URL,
    CONF_BATCH_SIZE,
    CONF_EVENT_STREAM,
    CONF_FLUSH_INTERVAL,
    CONF_LOG_STREAM,
    CONF_ORGANIZATION,
    CONF_PASSWORD,
    CONF_USERNAME,
    DEFAULT_BATCH_SIZE,
    DEFAULT_EVENT_STREAM,
    DEFAULT_FLUSH_INTERVAL,
    DEFAULT_LOG_STREAM,
    DEFAULT_ORGANIZATION,
)

_LOGGER = logging.getLogger(__name__)

CLIENT_TIMEOUT = aiohttp.ClientTimeout(total=15)


class OpenObserveClient:
    """Batches records and POSTs JSON arrays to OpenObserve /_json endpoints."""

    def __init__(self, hass: Any, entry: Any) -> None:
        self._hass = hass
        self._entry = entry
        opts = {**entry.data, **entry.options}

        base_url = opts[CONF_BASE_URL].rstrip("/")
        org = opts.get(CONF_ORGANIZATION, DEFAULT_ORGANIZATION)
        self._log_stream = opts.get(CONF_LOG_STREAM, DEFAULT_LOG_STREAM)
        self._event_stream = opts.get(CONF_EVENT_STREAM, DEFAULT_EVENT_STREAM)
        self._batch_size = int(opts.get(CONF_BATCH_SIZE, DEFAULT_BATCH_SIZE))
        self._flush_interval = float(opts.get(CONF_FLUSH_INTERVAL, DEFAULT_FLUSH_INTERVAL))

        self._log_url = f"{base_url}/api/{org}/{self._log_stream}/_json"
        self._event_url = f"{base_url}/api/{org}/{self._event_stream}/_json"

        username = opts[CONF_USERNAME]
        password = opts[CONF_PASSWORD]
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {token}",
        }

        self._lock = asyncio.Lock()
        self._log_buffer: list[dict[str, Any]] = []
        self._event_buffer: list[dict[str, Any]] = []
        self._disabled = False

        self.records_sent = 0
        self.last_flush_time: str | None = None
        self.last_error: str | None = None

    @property
    def log_url(self) -> str:
        return self._log_url

    @property
    def event_url(self) -> str:
        return self._event_url

    @staticmethod
    async def async_validate(hass: Any, data: dict[str, Any]) -> None:
        """Validate credentials and connectivity during config flow."""
        base_url = data[CONF_BASE_URL].rstrip("/")
        org = data.get(CONF_ORGANIZATION, DEFAULT_ORGANIZATION)
        log_stream = data.get(CONF_LOG_STREAM, DEFAULT_LOG_STREAM)
        url = f"{base_url}/api/{org}/{log_stream}/_json"
        username = data[CONF_USERNAME]
        password = data[CONF_PASSWORD]
        token = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {token}",
        }
        test_record = {
            "@timestamp": "1970-01-01T00:00:00Z",
            "service": "home-assistant",
            "app": "core",
            "record_type": "log",
            "level": "info",
            "message": "OpenObserve integration connectivity test",
        }
        session = async_get_clientsession(hass)
        async with session.post(
            url,
            json=[test_record],
            headers=headers,
            timeout=CLIENT_TIMEOUT,
        ) as resp:
            if resp.status in (401, 403):
                raise aiohttp.ClientResponseError(
                    resp.request_info,
                    resp.history,
                    status=resp.status,
                    message="Authentication failed",
                )
            if resp.status >= 400:
                body = await resp.text()
                raise aiohttp.ClientError(
                    f"OpenObserve returned HTTP {resp.status}: {body[:200]}"
                )

    async def validate_connection(self) -> None:
        """Send a test record to the log stream."""
        test_record = {
            "@timestamp": "1970-01-01T00:00:00Z",
            "service": "home-assistant",
            "app": "core",
            "record_type": "log",
            "level": "info",
            "message": "OpenObserve integration connectivity test",
        }
        session = async_get_clientsession(self._hass)
        async with session.post(
            self._log_url,
            json=[test_record],
            headers=self._headers,
            timeout=CLIENT_TIMEOUT,
        ) as resp:
            if resp.status in (401, 403):
                raise aiohttp.ClientResponseError(
                    resp.request_info,
                    resp.history,
                    status=resp.status,
                    message="Authentication failed",
                )
            if resp.status >= 400:
                body = await resp.text()
                raise aiohttp.ClientError(
                    f"OpenObserve returned HTTP {resp.status}: {body[:200]}"
                )

    def enqueue_log(self, record: dict[str, Any]) -> None:
        if self._disabled:
            return
        self._log_buffer.append(record)
        if len(self._log_buffer) >= self._batch_size:
            self._hass.async_create_task(self.flush())

    def enqueue_event(self, record: dict[str, Any]) -> None:
        if self._disabled:
            return
        self._event_buffer.append(record)
        if len(self._event_buffer) >= self._batch_size:
            self._hass.async_create_task(self.flush())

    async def flush_loop(self) -> None:
        """Periodically flush buffers."""
        try:
            while not self._disabled:
                await asyncio.sleep(self._flush_interval)
                await self.flush()
        except asyncio.CancelledError:
            pass

    async def flush(self) -> None:
        """Flush all buffered records."""
        log_records: list[dict[str, Any]] = []
        event_records: list[dict[str, Any]] = []

        async with self._lock:
            if self._log_buffer:
                log_records = self._log_buffer.copy()
                self._log_buffer.clear()
            if self._event_buffer:
                event_records = self._event_buffer.copy()
                self._event_buffer.clear()

        session = async_get_clientsession(self._hass)

        if log_records:
            await self._post_batch(session, self._log_url, log_records)

        if event_records:
            await self._post_batch(session, self._event_url, event_records)

    async def _post_batch(
        self,
        session: aiohttp.ClientSession,
        url: str,
        records: list[dict[str, Any]],
    ) -> None:
        try:
            async with session.post(
                url,
                json=records,
                headers=self._headers,
                timeout=CLIENT_TIMEOUT,
            ) as resp:
                if resp.status in (401, 403):
                    self.last_error = f"HTTP {resp.status}: authentication failed"
                    _LOGGER.warning(
                        "openobserve: authentication failed (%s), starting reauth",
                        resp.status,
                    )
                    self._entry.async_start_reauth(self._hass)
                    return
                if resp.status >= 400:
                    body = await resp.text()
                    self.last_error = f"HTTP {resp.status}: {body[:200]}"
                    _LOGGER.warning(
                        "openobserve: ingest failed (%s): %s",
                        resp.status,
                        body[:200],
                    )
                    return
                self.records_sent += len(records)
                self.last_error = None
                from datetime import UTC, datetime

                self.last_flush_time = datetime.now(tz=UTC).isoformat()
        except aiohttp.ClientError as err:
            self.last_error = str(err)
            _LOGGER.warning("openobserve: failed to send %d records: %s", len(records), err)
        except RuntimeError as err:
            if "Session is closed" in str(err):
                _LOGGER.debug(
                    "openobserve: session closed during shutdown, dropping %d records",
                    len(records),
                )
            else:
                self.last_error = str(err)
                _LOGGER.warning("openobserve: unexpected error: %s", err)

    async def disable_buffer(self) -> None:
        """Stop accepting new records and flush remaining."""
        self._disabled = True
        await self.flush()

    async def close(self) -> None:
        """Final flush."""
        await self.disable_buffer()
