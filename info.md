# OpenObserve

Ship Home Assistant **logs** and **bus events** to [OpenObserve](https://openobserve.ai/) for search, dashboards, and alerting.

## What gets sent

| Stream | Content |
|--------|---------|
| `home_assistant_logs` | Core / system logs (level filter in options) |
| `home_assistant_events` | Startup/shutdown, state changes, service calls (configurable) |

Records are batched (default: 50 records or 5 seconds). Use service `openobserve.flush` to force a send.

## Configuration

1. Add integration **OpenObserve**
2. Base URL (e.g. `http://openobserve:5080` on Docker, or your LAN host)
3. Organization, username, password, stream names

Sensitive keys in event payloads are redacted by default.

## Optional add-on

For `home-assistant.log` file lines on **Home Assistant OS**, see the Supervisor add-on:
https://github.com/Shaffer-Softworks/home-assistant-openobserve-addon

## Support

Issues: https://github.com/Shaffer-Softworks/Openobserve/issues
