#!/bin/bash

set -e
target="$1"
. ../utils.sh

cd "$target"

if make all; then
  green "Your kernel built successfully!"
  exit 100
fi

red "Your kernel failed to build!"
exit 0
