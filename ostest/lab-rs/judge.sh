#!/bin/bash

target="$1"
. ../utils.sh

cd "$target" || exit 2

run() {
  docker run --rm --mount type=bind,src="$target",dst=/app -w /app rust:1.62.1 "$@"
}

if ! run cargo build --release; then
  red "Your program failed to build."
  exit 0
fi

rm -rf lab_dir
run cargo run --release
ret=$?
if [ "$ret" -ne 0 ]; then
  red "Your program exited with code $ret."
  exit 20
fi

if ! [ -d lab_dir ]; then
  red "Your program didn't create the directory."
  exit 40
fi

exit 100
