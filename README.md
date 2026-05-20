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

## Test with Home Assistant (Docker / Portainer)

There are **two different pieces** in this repo:

| Piece | Runs in container HA? | Runs in HA OS / Supervisor? |
|-------|------------------------|-----------------------------|
| **HACS integration** (`custom_components/openobserve`) | Yes | Yes |
| **Log shipper add-on** (`openobserve_log_shipper`) | **No** | Yes (add-on store) |

When you asked to “deploy to Portainer,” only **OpenObserve** was deployed—not Home Assistant. The add-on cannot be tested in a plain `home-assistant` Docker image; it needs **Home Assistant OS** (Supervisor).

### Test stack (integration only)

Use [`deploy/portainer/docker-compose.ha-test.yml`](deploy/portainer/docker-compose.ha-test.yml) — **Home Assistant + OpenObserve** on one Docker network.

**From the repo root** (Docker running):

```bash
export ZO_ROOT_USER_PASSWORD='your-password'
docker compose -f deploy/portainer/docker-compose.ha-test.yml up -d
```

**In Portainer:** Stacks → Add stack → Web editor → paste that compose file → set `ZO_ROOT_USER_PASSWORD` → deploy from a **git clone** of this repo on the Docker host so the `custom_components` bind mount resolves.

After HA finishes starting (~2–5 min):

1. Open `http://<docker-host>:8123` and complete onboarding.
2. **Settings → Devices & services → Add integration → OpenObserve**
3. Use **Base URL** `http://openobserve:5080` (service name on the internal network—not `localhost`).
4. Org `default`, same email/password as `ZO_ROOT_USER_*`.
5. Trigger a log line or toggle a light, then search `home_assistant_logs` in OpenObserve.

To test the **log shipper add-on**, use a real HA OS machine (or your existing HA at `ha.shafferco.com`) and add the add-on from your add-on repository—not this Docker test stack.

## Deploy with Docker (containers only)

From the repo root:

```bash
export ZO_ROOT_USER_PASSWORD='your-password'
./deploy/docker/run.sh
```

- **OpenObserve:** http://localhost:5080  
- **Home Assistant:** http://localhost:8123 (onboarding on first visit)  
- **Integration URL in HA:** `http://openobserve:5080`

## Deploy OpenObserve only (Portainer / Docker)

Compose file: [`deploy/portainer/docker-compose.yml`](deploy/portainer/docker-compose.yml)

**Portainer (local stack):** Stacks → Add stack → paste compose → set environment variables from [`deploy/portainer/.env.example`](deploy/portainer/.env.example).

| Variable | Purpose |
|----------|---------|
| `ZO_ROOT_USER_EMAIL` | Admin login email |
| `ZO_ROOT_USER_PASSWORD` | Admin password (required on first start) |

UI: `http://<host>:5080` · OTLP gRPC: `5081`

A stack named **openobserve** is deployed on the connected Portainer **local** environment (Docker Desktop) when set up via the Portainer MCP integration.

### Login not working?

OpenObserve sets the root password **only on first boot** when the data volume is empty ([docs](https://openobserve.ai/docs/getting-started/)). Changing stack env vars later does not update the password.

1. In Portainer: **Stacks → openobserve → Stop**
2. **Volumes →** delete `openobserve_openobserve-data`
3. **Start** the stack again (same env vars as in `.env.example`)
4. Log in at `http://<docker-host>:5080` with that email and password

Current stack credentials (after reset): `admin@example.com` and the password from your Portainer stack env / `.env.example`.

## Development

```bash
# Run hassfest locally (requires Docker or HA dev env)
docker run --rm -v "$(pwd):/github/workspace" ghcr.io/home-assistant/hassfest
```

## Icon attribution

Integration and add-on icons are from [Dashboard Icons](https://dashboardicons.com/icons/open-observe) ([homarr-labs/dashboard-icons](https://github.com/homarr-labs/dashboard-icons), Apache-2.0). Source: `open-observe` PNG (512×512) via [jsDelivr CDN](https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/png/open-observe.png).

## License

MIT (integration code). Icon assets: Apache-2.0 per Dashboard Icons / homarr-labs.
