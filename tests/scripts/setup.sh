#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

PORT='8065'
API="http://127.0.0.1:${PORT}/api/v4"
CONTAINER="mattermost-mmemoji"

if ! docker info >/dev/null 2>&1; then
  echo 'Docker needs to installed and running!'
  exit 1
fi

echo "Creating test instance..."
docker run --detach \
  --name "${CONTAINER}" \
  --publish "${PORT}:8065" \
  --add-host dockerhost:127.0.0.1 \
  mattermost/mattermost-preview

echo "Waiting for instance to be ready..."
until curl -fs "${API}/system/ping" >/dev/null; do sleep 1; done

echo "Loading sample data..."
docker exec "${CONTAINER}" mattermost sampledata >/dev/null

echo 'Enabling Custom Emoji...'
# The `config` subcommand was added in 5.6
docker exec "${CONTAINER}" mattermost config \
  set ServiceSettings.EnableCustomEmoji true \
  --config=mattermost/config/config_docker.json >/dev/null

printf 'Your environment is ready!
The following users should have been created:

Username           Email                           Password
-----------------  ------------------------------  --------
sysadmin           sysadmin@sample.mattermost.com  sysadmin
user-1             user-1@sample.mattermost.com    user-1
samuel.tucker      user-2@sample.mattermost.com    user-2
rebecca.simpson    user-3@sample.mattermost.com    user-3
louise.mccoy       user-4@sample.mattermost.com    user-4
gloria.allen       user-5@sample.mattermost.com    user-5
adam.torres        user-6@sample.mattermost.com    user-6
jesse.welch        user-7@sample.mattermost.com    user-7
brandon.ford       user-8@sample.mattermost.com    user-8
denise.washington  user-9@sample.mattermost.com    user-9
chris.jonese       user-10@sample.mattermost.com   user-10
sandra.stone       user-11@sample.mattermost.com   user-11
elizabeth.gardner  user-12@sample.mattermost.com   user-12
kenneth.simmons    user-13@sample.mattermost.com   user-13
nancy.sanders      user-14@sample.mattermost.com   user-14

'

exit 0
