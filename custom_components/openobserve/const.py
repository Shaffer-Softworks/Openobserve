"""Constants for the OpenObserve integration."""

from homeassistant.const import Platform

DOMAIN = "openobserve"

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_BASE_URL = "base_url"
CONF_ORGANIZATION = "organization"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LOG_STREAM = "log_stream"
CONF_EVENT_STREAM = "event_stream"
CONF_LOG_LEVEL = "log_level"
CONF_BATCH_SIZE = "batch_size"
CONF_FLUSH_INTERVAL = "flush_interval"
CONF_EVENT_BASED_LOGGING = "event_based_logging"
CONF_LOG_HA_LIFECYCLE = "log_ha_lifecycle"
CONF_LOG_HA_STATE_CHANGES = "log_ha_state_changes"
CONF_LOG_HA_FULL_STATE_CHANGES = "log_ha_full_state_changes"
CONF_LOG_HA_CORE_ACTIVITY = "log_ha_core_activity"
CONF_LOG_HA_EVENT_BODY = "log_ha_event_body"
CONF_STATE_CHANGED_EXCLUDE = "state_changed_exclude"

DEFAULT_ORGANIZATION = "default"
DEFAULT_LOG_STREAM = "home_assistant_logs"
DEFAULT_EVENT_STREAM = "home_assistant_events"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_BATCH_SIZE = 50
DEFAULT_FLUSH_INTERVAL = 5
DEFAULT_EVENT_BASED_LOGGING = True

LIFECYCLE_EVENTS: list[str] = [
    "homeassistant_start",
    "homeassistant_started",
    "homeassistant_stop",
    "homeassistant_close",
    "homeassistant_final_write",
]

CORE_STATE_EVENTS: list[str] = [
    "state_changed",
]

CORE_ACTIVITY_EVENTS: list[str] = [
    "call_service",
    "automation_triggered",
    "script_started",
]

LOG_LEVELS: list[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

SERVICE_FLUSH = "flush"

REF_CANCEL_LISTENERS = "cancel_listeners"
REF_FLUSH_TASK = "flush_task"
REF_CLIENT = "client"
REF_LOG_HANDLER = "log_handler"

SECRET_KEYS = frozenset(
    {
        "password",
        "token",
        "api_key",
        "access_token",
        "refresh_token",
        "client_secret",
        "private_key",
        "authorization",
        "code",
    }
)
