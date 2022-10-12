#!/bin/bash

cd "$(realpath -m "$0"/../..)" || exit 1
. ./config.ini

mkdir -p /srv/gitlab-ce/conf
cp install/gitlab.rb /srv/gitlab-ce/conf/

docker run \
  --detach \
  --restart always \
  --name gl \
  --privileged \
  --hostname "$PUBLIC_HOST" \
  --publish "$GITLAB_SSH_PORT":22 \
  --publish "$GITLAB_HTTP_PORT":80 \
  --volume /srv/gitlab-ce/conf:/etc/gitlab:z \
  --volume /srv/gitlab-ce/logs:/var/log/gitlab:z \
  --volume /srv/gitlab-ce/data:/var/opt/gitlab:z \
  -e GITLAB_SKIP_UNMIGRATED_DATA_CHECK=true \
  -e GITLAB_ROOT_PASSWORD=w9uSjydOC1IIl5irALckxC8hrF \
  yrzr/gitlab-ce-arm64v8:latest

docker run \
	--detach \
	--restart always \
	--name stats \
	--volume /srv/stats:/data \
	-p 82:3000 \
	ghcr.io/muety/wakapi:latest

# docker exec -it gl cat /etc/gitlab/initial_root_password
