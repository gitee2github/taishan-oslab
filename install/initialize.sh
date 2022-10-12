#!/bin/bash

cd "$(realpath -m "$0"/../..)" || exit 1
. ./settings

if ! [ -e /opt/ostest ]; then
  ln -s /opt/oslab/ostest /opt/ostest 2>/dev/null
fi

mkdir -p keys
yes n | ssh-keygen -t rsa -f keys/id_rsa -P ''

docker run -d --restart always \
  --name osjudge \
  --hostname osjudge \
  -e GITLAB_CONTAINER_NAME="$GITLAB_CONTAINER_NAME" \
  -e GITLAB_SSH_PORT="$GITLAB_SSH_PORT" \
  -e GITLAB_GLOBAL_HOST="$GITLAB_GLOBAL_HOST" \
  -e GITLAB_CONTAINER_NAME="$GITLAB_CONTAINER_NAME" \
  -v /OSLAB:/OSLAB:ro \
  -v /opt/ostest:/opt/ostest \
  -v /var/run/docker.sock:/var/run/docker.sock \
  ostest

docker cp keys/id_rsa osjudge:/root/.ssh/
docker cp keys/id_rsa.pub osjudge:/root/.ssh/authorized_keys
docker cp keys/id_rsa "$GITLAB_CONTAINER_NAME":/opt/git_id_rsa

docker exec -u root "$GITLAB_CONTAINER_NAME" chown -R git:git /opt/git_id_rsa

ssh-keyscan -p "$GITLAB_SSH_PORT" "$GITLAB_GLOBAL_HOST" > known_hosts 2>/dev/null
python3 install/add-judge-key.py

docker run -d \
  --restart always \
  --name osboard \
  --hostname osboard \
  -v /opt/ostest:/opt/ostest \
  -v /opt/oslab:/opt/oslab \
  -v /opt/oslab/board.json:/config.json \
  -v "$STATS_DB":"$STATS_DB" \
  -p "$BOARD_PORT":80 \
  osboard -w 2
