# Home Assistant → OpenObserve

Forward Home Assistant logs and events to [OpenObserve](https://openobserve.ai/) using a HACS custom integration and an optional Supervisor add-on for log files.

## Components

| Component | Purpose |
|-----------|---------|
| **HACS integration** (`custom_components/openobserve`) | Core logs via `system_log` events; bus events (lifecycle, state changes, service calls) |
| **Add-on** (`openobserve_log_shipper`) | Tails `home-assistant.log` from `/config` and ships lines to OpenObserve |

## Suggested OpenObserve streams

| Stream | Source |
|--------|--------|
| `home_assistant_logs` | Integration |
| `home_assistant_events` | Integration |
| `home_assistant_supervisor` | Add-on |

Streams are created automatically on first ingest.

## Install (HACS custom repository)

1. In HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/Shaffer-Softworks/home-assistant-openobserve`
3. Category: **Integration**
4. Install **OpenObserve** and restart Home Assistant
5. **Settings → Devices & services → Add integration → OpenObserve**
6. Enter your OpenObserve URL (e.g. `http://10.20.0.54:5080`), organization (`default`), credentials, and stream names

### Options

- **Minimum log level** — filter core logs
- **Lifecycle / state / service events** — toggle event groups
- **Exclude patterns** — one glob per line (e.g. `sensor.*`) to reduce `state_changed` volume
- **Batch size / flush interval** — tuning for network and load

### Service

`openobserve.flush` — force-send buffered records immediately.

### Diagnostic sensors

- Records sent
- Last flush
- Last error

## Install (Supervisor add-on)

Add this repository to your Home Assistant add-on store, then install **OpenObserve Log Shipper**.

Configure:

| Option | Example |
|--------|---------|
| OpenObserve ingest URL | `http://10.20.0.54:5080/api/default/home_assistant_supervisor/_multi` |
| Username | your OpenObserve user |
| Password | your OpenObserve password |

The add-on mounts `/config` read-only and tails `home-assistant.log`.

## Verify in OpenObserve

```sql
SELECT * FROM home_assistant_logs ORDER BY _timestamp DESC LIMIT 10
```

```sql
SELECT * FROM home_assistant_events ORDER BY _timestamp DESC LIMIT 10
```

## Development

```bash
# Run hassfest locally (requires Docker or HA dev env)
docker run --rm -v "$(pwd):/github/workspace" ghcr.io/home-assistant/hassfest
```

## License

MIT
