# Home Assistant OpenObserve (HACS integration)

Forward Home Assistant core logs and bus events to [OpenObserve](https://openobserve.ai/) using a HACS custom integration.

**Optional:** [Home Assistant OpenObserve Log Shipper](https://github.com/Shaffer-Softworks/home-assistant-openobserve-addon) (Supervisor add-on) for `home-assistant.log` file shipping.

## Streams

| Stream | Source |
|--------|--------|
| `home_assistant_logs` | Core / system logs |
| `home_assistant_events` | Lifecycle, state changes, service calls |

Streams are created on first ingest.

## Install (HACS)

1. HACS → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/Shaffer-Softworks/Openobserve` (or use **default** HACS store after inclusion)
3. Install **OpenObserve** and restart Home Assistant
4. **Settings → Devices & services → Add integration → OpenObserve**
5. Base URL (e.g. `http://10.20.0.54:5080` or `http://openobserve:5080` on Docker), org `default`, credentials, stream names

### Manual install

Download the [latest release](https://github.com/Shaffer-Softworks/Openobserve/releases) zip, extract it, and move the `openobserve` folder into `custom_components/` in your Home Assistant config.

## Releases

Maintainers publish versions from **Actions → Create release** (workflow dispatch). The workflow:

1. Bumps `custom_components/openobserve/manifest.json`
2. Pushes branch `release/vX.Y.Z` and tag `vX.Y.Z`
3. Attaches **`openobserve.zip`** for HACS `zip_release`
4. Opens a PR to merge the manifest bump into `main`

Optional repo secret **`WORKFLOW_TRIGGER_TOKEN`** (PAT with `contents`, `pull_requests`, and `actions`) avoids stuck PR checks when GitHub suppresses workflows triggered by `GITHUB_TOKEN`.

### Options

- Minimum log level, event toggles, exclude globs (`sensor.*`)
- Batch size (default 50), flush interval (default 5 seconds)

### Service

`openobserve.flush` — force-send buffered records.

### Diagnostic sensors

Records sent, last flush, last error.

## Docker test (integration only)

```bash
export ZO_ROOT_USER_PASSWORD='your-password'
./deploy/docker/run.sh
```

- OpenObserve: http://localhost:5080
- Home Assistant: http://localhost:8123
- Integration URL: **`http://openobserve:5080`** (not `localhost`)

See [`deploy/portainer/docker-compose.ha-test.yml`](deploy/portainer/docker-compose.ha-test.yml) for a combined compose file.

## Verify

```sql
SELECT * FROM home_assistant_logs ORDER BY _timestamp DESC LIMIT 10
```

```sql
SELECT * FROM home_assistant_events ORDER BY _timestamp DESC LIMIT 10
```

## Development

```bash
docker run --rm -v "$(pwd):/github/workspace" ghcr.io/home-assistant/hassfest
```

## Icon attribution

[Dashboard Icons — open-observe](https://dashboardicons.com/icons/open-observe) (homarr-labs/dashboard-icons, Apache-2.0).

## License

MIT (integration code). Icon assets: Apache-2.0 per Dashboard Icons.
