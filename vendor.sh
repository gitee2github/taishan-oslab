#!/bin/bash

set -e

venv="$(mktemp -d)"
python3 -m venv "$venv"
"$venv/bin/pip" install -U pip wheel setuptools
"$venv/bin/pip" install -U -r requirements.txt

site="$venv/lib/python3.7/site-packages"
find "$site" | grep -E "(/__pycache__$|\.pyc$|\.pyo$|\.dist-info$)" | xargs rm -rf
tar czf vendor.tar.gz -C "$site" .
rm -r "$venv"
