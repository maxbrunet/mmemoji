#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${MATTERMOST_HOST:-127.0.0.1}"
PORT="${MATTERMOST_PORT:-8065}"
API="http://${HOST}:${PORT}/api/v4"
CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"
# Version tags do not seem to be pushed consistently, `latest` may be more recent
TAG="${MATTERMOST_VERSION:-7.9.1@sha256:7d8be9ef3d13fd5cd7794add83030f93929da102d078ad07b33a2920fe3891f0}"

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
