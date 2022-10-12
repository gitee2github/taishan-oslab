#!/bin/bash

set -e
docker build -t os2022 docker/oe
docker build -t ostest docker/judge
docker build -t osboard docker/board
