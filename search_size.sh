#!/usr/bin/env bash

for site in shonenjumpplus comic-days; do
  base="https://${site}.com"
  curl -s "$base" | grep -oP "${base}/episode/\d+" |
  while read episode;do
    echo "${episode}.json"
    curl -s "${episode}.json" | grep -oP '("height"|"width"):\d+' |
    sort | uniq
  done
done
