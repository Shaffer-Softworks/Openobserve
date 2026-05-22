"""Config flow for OpenObserve."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .client import OpenObserveClient
from .const import (
    CONF_BASE_URL,
    CONF_BATCH_SIZE,
    CONF_CAPTURE_EVENTS,
    CONF_CAPTURE_LOGS,
    CONF_EVENT_BASED_LOGGING,
    CONF_EVENT_STREAM,
    CONF_FLUSH_INTERVAL,
    CONF_LOG_HA_CORE_ACTIVITY,
    CONF_LOG_HA_EVENT_BODY,
    CONF_LOG_HA_FULL_STATE_CHANGES,
    CONF_LOG_HA_LIFECYCLE,
    CONF_LOG_HA_STATE_CHANGES,
    CONF_LOG_LEVEL,
    CONF_LOG_STREAM,
    CONF_ORGANIZATION,
    CONF_PASSWORD,
    CONF_STATE_CHANGED_EXCLUDE,
    CONF_USERNAME,
    DEFAULT_BATCH_SIZE,
    DEFAULT_CAPTURE_EVENTS,
    DEFAULT_CAPTURE_LOGS,
    DEFAULT_EVENT_BASED_LOGGING,
    DEFAULT_EVENT_STREAM,
    DEFAULT_FLUSH_INTERVAL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_STREAM,
    DEFAULT_ORGANIZATION,
    DOMAIN,
    LOG_LEVELS,
)

_LOGGER = logging.getLogger(__name__)

def _text_selector(*, password: bool = False, multiline: bool = False) -> TextSelector:
    return TextSelector(
        TextSelectorConfig(
            type=TextSelectorType.PASSWORD if password else TextSelectorType.TEXT,
            multiline=multiline,
        )
    )


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL): TextSelector(
            TextSelectorConfig(type=TextSelectorType.URL)
        ),
        vol.Required(CONF_ORGANIZATION, default=DEFAULT_ORGANIZATION): _text_selector(),
        vol.Required(CONF_USERNAME): _text_selector(),
        vol.Required(CONF_PASSWORD): _text_selector(password=True),
        vol.Required(CONF_LOG_STREAM, default=DEFAULT_LOG_STREAM): _text_selector(),
        vol.Required(CONF_EVENT_STREAM, default=DEFAULT_EVENT_STREAM): _text_selector(),
    }
)


def _options_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_CAPTURE_LOGS,
                default=defaults.get(CONF_CAPTURE_LOGS, DEFAULT_CAPTURE_LOGS),
            ): BooleanSelector(),
            vol.Optional(
                CONF_CAPTURE_EVENTS,
                default=defaults.get(CONF_CAPTURE_EVENTS, DEFAULT_CAPTURE_EVENTS),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_LEVEL, default=defaults.get(CONF_LOG_LEVEL, DEFAULT_LOG_LEVEL)
            ): SelectSelector(
                SelectSelectorConfig(options=LOG_LEVELS, mode=SelectSelectorMode.DROPDOWN)
            ),
            vol.Optional(
                CONF_EVENT_BASED_LOGGING,
                default=defaults.get(CONF_EVENT_BASED_LOGGING, DEFAULT_EVENT_BASED_LOGGING),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_HA_LIFECYCLE,
                default=defaults.get(CONF_LOG_HA_LIFECYCLE, True),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_HA_STATE_CHANGES,
                default=defaults.get(CONF_LOG_HA_STATE_CHANGES, True),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_HA_FULL_STATE_CHANGES,
                default=defaults.get(CONF_LOG_HA_FULL_STATE_CHANGES, False),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_HA_CORE_ACTIVITY,
                default=defaults.get(CONF_LOG_HA_CORE_ACTIVITY, True),
            ): BooleanSelector(),
            vol.Optional(
                CONF_LOG_HA_EVENT_BODY,
                default=defaults.get(CONF_LOG_HA_EVENT_BODY, False),
            ): BooleanSelector(),
            vol.Optional(
                CONF_STATE_CHANGED_EXCLUDE,
                default=defaults.get(CONF_STATE_CHANGED_EXCLUDE, "sensor.*\ndevice_tracker.*"),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)),
            vol.Optional(
                CONF_BATCH_SIZE,
                default=defaults.get(CONF_BATCH_SIZE, DEFAULT_BATCH_SIZE),
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=500, step=1, mode=NumberSelectorMode.BOX)
            ),
            vol.Optional(
                CONF_FLUSH_INTERVAL,
                default=defaults.get(CONF_FLUSH_INTERVAL, DEFAULT_FLUSH_INTERVAL),
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=300, step=1, mode=NumberSelectorMode.BOX)
            ),
        }
    )


class OpenObserveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OpenObserve."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_BASE_URL] = user_input[CONF_BASE_URL].rstrip("/")
            await self.async_set_unique_id(user_input[CONF_BASE_URL])
            self._abort_if_unique_id_configured()

            try:
                await OpenObserveClient.async_validate(self.hass, user_input)
            except aiohttp.ClientResponseError:
                errors["base"] = "invalid_auth"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error validating OpenObserve")
                errors["base"] = "unknown"

            if not errors:
                return self.async_create_entry(
                    title="OpenObserve",
                    data=user_input,
                    options={
                        CONF_CAPTURE_LOGS: DEFAULT_CAPTURE_LOGS,
                        CONF_CAPTURE_EVENTS: DEFAULT_CAPTURE_EVENTS,
                        CONF_LOG_LEVEL: DEFAULT_LOG_LEVEL,
                        CONF_EVENT_BASED_LOGGING: DEFAULT_EVENT_BASED_LOGGING,
                        CONF_LOG_HA_LIFECYCLE: True,
                        CONF_LOG_HA_STATE_CHANGES: True,
                        CONF_LOG_HA_FULL_STATE_CHANGES: False,
                        CONF_LOG_HA_CORE_ACTIVITY: True,
                        CONF_LOG_HA_EVENT_BODY: False,
                        CONF_STATE_CHANGED_EXCLUDE: "sensor.*\ndevice_tracker.*",
                        CONF_BATCH_SIZE: DEFAULT_BATCH_SIZE,
                        CONF_FLUSH_INTERVAL: DEFAULT_FLUSH_INTERVAL,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @config_entries.callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlow:
        """Get the options flow."""
        return OpenObserveOptionsFlowHandler(config_entry)


class OpenObserveOptionsFlowHandler(OptionsFlow):
    """Handle options (HA 2025+: do not assign self.config_entry — read-only)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults: dict[str, Any] = {
            CONF_CAPTURE_LOGS: DEFAULT_CAPTURE_LOGS,
            CONF_CAPTURE_EVENTS: DEFAULT_CAPTURE_EVENTS,
            CONF_LOG_LEVEL: DEFAULT_LOG_LEVEL,
            CONF_EVENT_BASED_LOGGING: DEFAULT_EVENT_BASED_LOGGING,
            CONF_LOG_HA_LIFECYCLE: True,
            CONF_LOG_HA_STATE_CHANGES: True,
            CONF_LOG_HA_FULL_STATE_CHANGES: False,
            CONF_LOG_HA_CORE_ACTIVITY: True,
            CONF_LOG_HA_EVENT_BODY: False,
            CONF_STATE_CHANGED_EXCLUDE: "sensor.*\ndevice_tracker.*",
            CONF_BATCH_SIZE: DEFAULT_BATCH_SIZE,
            CONF_FLUSH_INTERVAL: DEFAULT_FLUSH_INTERVAL,
        }
        defaults.update(self._config_entry.options)
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(defaults),
        )
