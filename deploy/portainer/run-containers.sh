#!/usr/bin/env bash
# Standalone containers (no Compose stack). Run on the Docker host (e.g. via Portainer console or SSH).
set -euo pipefail

NETWORK="${NETWORK:-openobserve_default}"
O2_EMAIL="${ZO_ROOT_USER_EMAIL:-admin@example.com}"
O2_PASS="${ZO_ROOT_USER_PASSWORD:?Set ZO_ROOT_USER_PASSWORD}"
REPO="${OPENOBSERVE_REPO:-/Users/michaelshaffer/Openobserve}"

docker network create "$NETWORK" 2>/dev/null || true

# OpenObserve
docker rm -f openobserve 2>/dev/null || true
docker run -d \
  --name openobserve \
  --restart unless-stopped \
  --network "$NETWORK" \
  -p 5080:5080 \
  -p 5081:5081 \
  -v openobserve-data:/data \
  -e ZO_DATA_DIR=/data \
  -e "ZO_ROOT_USER_EMAIL=$O2_EMAIL" \
  -e "ZO_ROOT_USER_PASSWORD=$O2_PASS" \
  public.ecr.aws/zinclabs/openobserve:latest

# Home Assistant (integration bind-mounted from repo)
docker rm -f homeassistant 2>/dev/null || true
docker run -d \
  --name homeassistant \
  --restart unless-stopped \
  --network "$NETWORK" \
  -p 8123:8123 \
  -v homeassistant-config:/config \
  -v "$REPO/custom_components/openobserve:/config/custom_components/openobserve:ro" \
  -e TZ="${TZ:-America/New_York}" \
  ghcr.io/home-assistant/home-assistant:stable

echo "OpenObserve: http://<host>:5080  (login: $O2_EMAIL)"
echo "Home Assistant: http://<host>:8123"
echo "Integration URL: http://openobserve:5080"
