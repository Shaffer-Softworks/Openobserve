"""Diagnostic sensors for OpenObserve."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .client import OpenObserveClient
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OpenObserve diagnostic sensors."""
    client: OpenObserveClient = entry.runtime_data
    async_add_entities(
        [
            OpenObserveRecordsSentSensor(entry, client),
            OpenObserveLastFlushSensor(entry, client),
            OpenObserveLastErrorSensor(entry, client),
        ]
    )


class OpenObserveSensorBase(SensorEntity):
    """Base sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = True
    _attr_available = True

    def __init__(
        self,
        entry: ConfigEntry,
        client: OpenObserveClient,
        *,
        unique_suffix: str,
    ) -> None:
        self._client = client
        self._attr_unique_id = f"{entry.entry_id}_{unique_suffix}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "OpenObserve",
            "manufacturer": "Shaffer Softworks",
            "model": "Log Shipper",
        }

    @property
    def suggested_poll_interval(self) -> timedelta:
        return timedelta(seconds=30)


class OpenObserveRecordsSentSensor(OpenObserveSensorBase):
    """Total records sent."""

    def __init__(self, entry: ConfigEntry, client: OpenObserveClient, **kwargs: object) -> None:
        super().__init__(entry, client, unique_suffix="records_sent")

    _attr_name = "Records sent"
    _attr_icon = "mdi:counter"
    _attr_native_value: int = 0

    @property
    def native_value(self) -> int:
        return self._client.records_sent


class OpenObserveLastFlushSensor(OpenObserveSensorBase):
    """Last successful flush time."""

    def __init__(self, entry: ConfigEntry, client: OpenObserveClient, **kwargs: object) -> None:
        super().__init__(entry, client, unique_suffix="last_flush")

    _attr_name = "Last flush"
    _attr_icon = "mdi:clock-check"

    @property
    def native_value(self) -> str | None:
        return self._client.last_flush_time


class OpenObserveLastErrorSensor(OpenObserveSensorBase):
    """Last ingest error."""

    def __init__(self, entry: ConfigEntry, client: OpenObserveClient, **kwargs: object) -> None:
        super().__init__(entry, client, unique_suffix="last_error")

    _attr_name = "Last error"
    _attr_icon = "mdi:alert-circle"

    @property
    def native_value(self) -> str | None:
        return self._client.last_error
