#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"

docker exec -i "${CONTAINER}" bash -e <<EOF
  # Chicken or the egg problem: It is required to be logged in
  # to generate sample data, even with --bulk
  if ! mmctl auth current >/dev/null 2>&1; then
    mmctl auth login http://localhost:8065 \
      --name local-server \
      --username sysadmin \
      --password-file /dev/stdin \
      >/dev/null <<<'Sys@dmin-sample1'
  fi

  mmctl sampledata \
    --bulk /dev/stdout \
    --channel-memberships 0 \
    --channels-per-team 0 \
    --direct-channels 0 \
    --group-channels 0 \
    --guests 0 \
    --posts-per-channel 0 \
    --posts-per-direct-channel 0 \
    --posts-per-group-channel 0 \
    --team-memberships 1 \
    --teams 1 \
    --users 2
EOF
