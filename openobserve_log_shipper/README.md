# OpenObserve Log Shipper (Home Assistant Add-on)

Tails `home-assistant.log` from the Home Assistant config mount and forwards lines to OpenObserve using Fluent Bit.

## Configuration

| Option | Description |
|--------|-------------|
| `openobserve_url` | Full ingest URL, e.g. `http://10.20.0.54:5080/api/default/home_assistant_supervisor/_multi` |
| `openobserve_username` | Basic auth username |
| `openobserve_password` | Basic auth password |
| `log_path` | Path inside the container (default `/config/home-assistant.log`) |

Use `/_multi` (NDJSON) for Fluent Bit `json_lines` output. The integration uses `/_json` (JSON array) instead.

## Publishing

Add this folder to your Home Assistant add-on repository and bump `repository.yaml`.
