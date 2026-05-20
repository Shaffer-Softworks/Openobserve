#!/usr/bin/env bash
# Deploy OpenObserve + Home Assistant as plain Docker containers (no Compose stack).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

export OPENOBSERVE_REPO="${OPENOBSERVE_REPO:-$REPO_ROOT}"
export ZO_ROOT_USER_EMAIL="${ZO_ROOT_USER_EMAIL:-admin@example.com}"
export ZO_ROOT_USER_PASSWORD="${ZO_ROOT_USER_PASSWORD:?Set ZO_ROOT_USER_PASSWORD}"

exec "$REPO_ROOT/deploy/portainer/run-containers.sh"
