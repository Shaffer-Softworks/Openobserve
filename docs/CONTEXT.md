# Project context — HACS integration repo

Split from monorepo on 2026-05-20. **Add-on** lives in [home-assistant-openobserve-addon](https://github.com/Shaffer-Softworks/home-assistant-openobserve-addon).

## Repo scope

- `custom_components/openobserve/` only (domain `openobserve`, v0.1.2+)
- HACS: `hacs.json`, hassfest + hacs/action
- Docker test: `deploy/docker/run.sh`

## Config flow (HA 2025.12+)

`OpenObserveOptionsFlowHandler`: use `self._config_entry`, not `self.config_entry = …`, no `super().__init__(config_entry)`.

## Docker test

Integration URL: `http://openobserve:5080`. Containers: `openobserve`, `homeassistant` via `deploy/docker/run.sh`.

## Ingest

Flush every 5s or 50 records. Streams: `home_assistant_logs`, `home_assistant_events`.

## Production LAN

OpenObserve at `http://10.20.0.54:5080` for production HA; local Docker is dev only.
