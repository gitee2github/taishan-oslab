#!/bin/bash
rsync -rvz --progress . ecs:/opt/oslab/ --exclude sync --exclude dep --exclude .git --exclude ostest --exclude known_hosts --exclude venv --exclude .vent --exclude oscore --exclude docs --exclude build
