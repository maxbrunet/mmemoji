#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${MATTERMOST_HOST:-127.0.0.1}"
PORT="${MATTERMOST_PORT:-8065}"
API="http://${HOST}:${PORT}/api/v4"
CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"
# Version tags do not seem to be pushed consistently, `latest` may be more recent
TAG="${MATTERMOST_VERSION:-6.0.0@sha256:f3aff08d0c1b1bc7726ad42f56630f36021660695d99b22d96cd4946b67455c9}"

if ! docker info >/dev/null 2>&1; then
  echo '>>> Docker needs to installed and running!'
  exit 1
fi

echo '>>> Creating test instance...'
docker run --detach \
  --name "${CONTAINER}" \
  --env MM_SERVICESETTINGS_ENABLECUSTOMEMOJI=true \
  --publish "${HOST}:${PORT}:8065" \
  --add-host dockerhost:127.0.0.1 \
  "docker.io/mattermost/mattermost-preview:${TAG}"

echo '>>> Waiting for instance to be ready...'
until curl -fs "${API}/system/ping" >/dev/null; do sleep 1; done

echo '>>> Loading sample data...'
docker exec -i mattermost-mmemoji mattermost \
  --config mattermost/config/config_docker.json \
  import bulk /dev/stdin --apply < "${SCRIPT_DIR}/sampledata.json"

printf '>>> Your environment is ready!
>>> The following users should have been created:

Username           Email                           Password
-----------------  ------------------------------  --------
sysadmin           sysadmin@sample.mattermost.com  Sys@dmin-sample1
user-1             user-1@sample.mattermost.com    SampleUs@r-1

'

exit 0
