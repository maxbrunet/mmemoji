#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${MATTERMOST_CONTAINER:-mattermost-mmemoji}"

docker exec -i "${CONTAINER}" bash <<EOF
  mattermost sampledata --bulk /sampledata.json \
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
    --users 2 1>&2
  cat /sampledata.json
EOF
