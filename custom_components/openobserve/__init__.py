"""The OpenObserve integration."""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any

from homeassistant.components.system_log import EVENT_SYSTEM_LOG
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP, Platform
from homeassistant.core import EVENT_HOMEASSISTANT_CLOSE, EVENT_HOMEASSISTANT_FINAL_WRITE, HomeAssistant, Event
from homeassistant.helpers import config_validation as cv

from .client import OpenObserveClient
from .const import (
    CONF_EVENT_BASED_LOGGING,
    CONF_LOG_HA_CORE_ACTIVITY,
    CONF_LOG_HA_EVENT_BODY,
    CONF_LOG_HA_FULL_STATE_CHANGES,
    CONF_LOG_HA_LIFECYCLE,
    CONF_LOG_HA_STATE_CHANGES,
    CONF_LOG_LEVEL,
    CONF_STATE_CHANGED_EXCLUDE,
    CORE_ACTIVITY_EVENTS,
    CORE_STATE_EVENTS,
    DOMAIN,
    LIFECYCLE_EVENTS,
    REF_CANCEL_LISTENERS,
    REF_CLIENT,
    REF_FLUSH_TASK,
    REF_LOG_HANDLER,
    SERVICE_FLUSH,
)
from .handler import ha_event_to_record, system_log_to_record
from .util import entity_matches_exclude
from .log_handler import ExportingLogHandler

_LOGGER = logging.getLogger(__name__)

type OpenObserveConfigEntry = ConfigEntry[OpenObserveClient]

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: OpenObserveConfigEntry) -> bool:
    """Set up OpenObserve from a config entry."""
    opts = {**entry.data, **entry.options}
    client = OpenObserveClient(hass, entry)
    entry.runtime_data = client

    min_level_name = opts.get(CONF_LOG_LEVEL, "INFO")
    min_level = getattr(logging, min_level_name, logging.INFO)

    async def _flush_on_stop(_: Any) -> None:
        await client.disable_buffer()

    cancel_listeners: list[Any] = [
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _flush_on_stop),
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_CLOSE, _flush_on_stop),
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_FINAL_WRITE, _flush_on_stop),
        entry.add_update_listener(_async_update_listener),
    ]

    def _log_level_ok(level_name: str) -> bool:
        level = getattr(logging, level_name.upper(), logging.INFO)
        return level >= min_level

    def handle_system_log(event: Event) -> None:
        data = event.data
        if not _log_level_ok(data.get("level", "INFO")):
            return
        client.enqueue_log(system_log_to_record(data))

    log_handler: ExportingLogHandler | None = None
    event_based = bool(opts.get(CONF_EVENT_BASED_LOGGING, True))
    if event_based:
        cancel_listeners.append(
            hass.bus.async_listen(EVENT_SYSTEM_LOG, handle_system_log)
        )
    else:
        log_handler = ExportingLogHandler(hass, client)
        log_handler.setLevel(min_level)
        logging.root.addHandler(log_handler)

    exclude_patterns = [
        p.strip()
        for p in opts.get(CONF_STATE_CHANGED_EXCLUDE, "").split("\n")
        if p.strip()
    ]
    include_body = bool(opts.get(CONF_LOG_HA_EVENT_BODY, False))

    def make_event_handler(
        event_type: str,
        *,
        state_only: bool = True,
    ):
        def _handler(event: Event) -> None:
            if event_type == "state_changed":
                entity_id = event.data.get("entity_id")
                if entity_matches_exclude(entity_id, exclude_patterns):
                    return
            record = ha_event_to_record(
                event,
                state_only=state_only,
                include_body=include_body,
            )
            client.enqueue_event(record)

        return _handler

    if opts.get(CONF_LOG_HA_LIFECYCLE):
        for et in LIFECYCLE_EVENTS:
            cancel_listeners.append(
                hass.bus.async_listen(et, make_event_handler(et))
            )
        _LOGGER.info("openobserve: listening for lifecycle events")

    if opts.get(CONF_LOG_HA_STATE_CHANGES):
        for et in CORE_STATE_EVENTS:
            cancel_listeners.append(
                hass.bus.async_listen(
                    et, make_event_handler(et, state_only=True)
                )
            )
        _LOGGER.info("openobserve: listening for state changes (summary)")

    if opts.get(CONF_LOG_HA_FULL_STATE_CHANGES):
        for et in CORE_STATE_EVENTS:
            cancel_listeners.append(
                hass.bus.async_listen(
                    et, make_event_handler(et, state_only=False)
                )
            )
        _LOGGER.info("openobserve: listening for state changes (full)")

    if opts.get(CONF_LOG_HA_CORE_ACTIVITY):
        for et in CORE_ACTIVITY_EVENTS:
            cancel_listeners.append(
                hass.bus.async_listen(et, make_event_handler(et))
            )
        _LOGGER.info("openobserve: listening for core activity events")

    flush_task = asyncio.create_task(client.flush_loop())

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        REF_CANCEL_LISTENERS: cancel_listeners,
        REF_FLUSH_TASK: flush_task,
        REF_CLIENT: client,
        REF_LOG_HANDLER: log_handler,
    }

    if not hass.services.has_service(DOMAIN, SERVICE_FLUSH):

        async def handle_flush(call: Any) -> None:
            for entry_data in hass.data[DOMAIN].values():
                await entry_data[REF_CLIENT].flush()

        hass.services.async_register(
            DOMAIN,
            SERVICE_FLUSH,
            handle_flush,
            schema=cv.make_entity_service_schema({}),
        )

    _LOGGER.info(
        "openobserve: forwarding logs to %s and events to %s",
        client.log_url,
        client.event_url,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: OpenObserveConfigEntry) -> bool:
    """Unload OpenObserve."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if data is None:
        return unload_ok

    for cancel in data.get(REF_CANCEL_LISTENERS, []):
        with contextlib.suppress(Exception):
            cancel()

    handler = data.get(REF_LOG_HANDLER)
    if handler is not None:
        logging.root.removeHandler(handler)

    flush_task = data.get(REF_FLUSH_TASK)
    if flush_task:
        flush_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await flush_task

    client: OpenObserveClient | None = data.get(REF_CLIENT)
    if client:
        await client.close()

    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, SERVICE_FLUSH)

    _LOGGER.info("openobserve: unloaded")
    return unload_ok
