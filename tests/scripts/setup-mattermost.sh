#!/usr/bin/env bash
set -euo pipefail

HOST="${MATTERMOST_HOST:-127.0.0.1}"
PORT="${MATTERMOST_PORT:-8065}"
API="http://${HOST}:${PORT}/api/v4"
CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"
# Version tags do not seem to be pushed consistently, `latest` may be more recent
TAG="${MATTERMOST_VERSION:-10.10.0@sha256:e9c553b36561be0f3f8006d2386f21868b97f0dcfe6a32594d8fa9cea901a4ca}"

if ! docker info >/dev/null 2>&1; then
  echo '>>> Docker needs to installed and running!'
  exit 1
fi

echo '>>> Creating test instance...'
docker run --detach \
  --name "${CONTAINER}" \
  --env MM_SERVICESETTINGS_ENABLECUSTOMEMOJI=true \
  --env MM_SERVICESETTINGS_ENABLELOCALMODE=true \
  --publish "${HOST}:${PORT}:8065" \
  --add-host dockerhost:127.0.0.1 \
  "docker.io/mattermost/mattermost-preview:${TAG}"

echo '>>> Waiting for instance to be ready...'
until curl -fs "${API}/system/ping" >/dev/null; do sleep 1; done

echo '>>> Loading sample data...'
docker exec "${CONTAINER}" mmctl --local sampledata \
  --channel-memberships 1 \
  --channels-per-team 1 \
  --direct-channels 0 \
  --group-channels 0 \
  --guests 0 \
  --posts-per-channel 0 \
  --posts-per-direct-channel 0 \
  --posts-per-group-channel 0 \
  --team-memberships 1 \
  --teams 1 \
  --users 2

printf '>>> Your environment is ready!
>>> The following users should have been created:

Username           Email                           Password
-----------------  ------------------------------  --------
sysadmin           sysadmin@sample.mattermost.com  Sys@dmin-sample1
user-1             user-1@sample.mattermost.com    SampleUs@r-1

'

exit 0
