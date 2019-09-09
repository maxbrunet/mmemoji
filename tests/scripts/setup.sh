#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${MATTERMOST_PORT:-8065}"
API="http://127.0.0.1:${PORT}/api/v4"
CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"
TAG="${MATTERMOST_VERSION:-latest}"

if ! docker info >/dev/null 2>&1; then
  echo '>>> Docker needs to installed and running!'
  exit 1
fi

echo '>>> Creating test instance...'
docker run --detach \
  --name "${CONTAINER}" \
  --publish "${PORT}:8065" \
  --add-host dockerhost:127.0.0.1 \
  "mattermost/mattermost-preview:${TAG}"

echo '>>> Waiting for instance to be ready...'
until curl -fs "${API}/system/ping" >/dev/null; do sleep 1; done

echo '>>> Loading sample data...'
docker exec -i mattermost-mmemoji mattermost import bulk /dev/stdin --apply < "${SCRIPT_DIR}/sampledata.json"

echo '>>> Enabling Custom Emoji...'
# The `config` subcommand was added in 5.6
docker exec "${CONTAINER}" mattermost config \
  set ServiceSettings.EnableCustomEmoji true \
  --config=mattermost/config/config_docker.json >/dev/null

printf '>>> Your environment is ready!
>>> The following users should have been created:

Username           Email                           Password
-----------------  ------------------------------  --------
sysadmin           sysadmin@sample.mattermost.com  Sys@dmin-sample1
user-1             user-1@sample.mattermost.com    SampleUs@r-1

'

exit 0
