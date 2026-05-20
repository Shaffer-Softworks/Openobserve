# Project context (saved 2026-05-20)

## What this repo is

Home Assistant → OpenObserve: HACS custom integration plus optional Supervisor add-on.

| Component | Path | Purpose |
|-----------|------|---------|
| Integration | `custom_components/openobserve/` | Core logs + bus events → OpenObserve `/_json` |
| Add-on | `openobserve_log_shipper/` | Tail `home-assistant.log` → `/_multi` (HA OS only) |
| Docker deploy | `deploy/docker/run.sh` | Standalone `openobserve` + `homeassistant` containers |

## Current version

`0.1.2` — config flow fix for HA 2025.12+ (`_config_entry`, no `super().__init__` on OptionsFlow).

## Local Docker test (working setup)

```bash
export ZO_ROOT_USER_PASSWORD='your-password'
./deploy/docker/run.sh
```

| Service | URL | Notes |
|---------|-----|--------|
| OpenObserve | http://localhost:5080 | Login: `admin@example.com` + stack password |
| Home Assistant | http://localhost:8123 | Onboarding on first visit |
| Integration URL in HA | `http://openobserve:5080` | Docker DNS name, not `localhost` |

Containers: `openobserve`, `homeassistant`. Network: `openobserve_default`. Volumes: `openobserve-data`, `homeassistant-config`.

## Ingest behavior

- Buffers logs and events separately
- Flushes every **5 seconds** or when **50** records queued (configurable in integration options)
- Streams: `home_assistant_logs`, `home_assistant_events`
- Service: `openobserve.flush` forces send
- Diagnostic sensors: records sent, last flush, last error

## OpenObserve password gotcha

Root credentials from env vars apply **only on first start** with empty `openobserve-data` volume. To reset: stop container, delete volume, start again.

## Config flow 500 fix (history)

HA logs showed:

- `AttributeError: property 'config_entry' ... has no setter`
- `TypeError: object.__init__() takes exactly one argument` after `super().__init__(config_entry)`

Fix: store `self._config_entry` only; use TextSelectors in user step schema.

## Production

LAN OpenObserve at `http://10.20.0.54:5080` (separate from local Docker test). Real HA instance for add-on testing (not container HA).

## Icons

From [dashboardicons.com/icons/open-observe](https://dashboardicons.com/icons/open-observe) via homarr-labs/dashboard-icons CDN.

## Not in scope

- OTLP exporter
- HACS default store PR (optional later)
- Cloning openobserve/openobserve server source into this repo
