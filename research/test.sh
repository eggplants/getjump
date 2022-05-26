#!/usr/bin/env bash

set -euo pipefail

if ! command -v feh getjump &> /dev/null; then
  echo "install: feh, getjump" >&2
  exit 1
fi

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <url>"
  exit 1
fi

getjump "$1" -d img -o -f && feh -Z. img/*/*
rm -rf img
