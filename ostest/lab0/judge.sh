#!/bin/bash

target="$1"
. ../utils.sh

if [ -f "$target/answer" ]; then
  green "ok!"
  exit 100
fi

red "no answer!"
exit 0
