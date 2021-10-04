#!/usr/bin/env bash

# Usage
# $ ./search_size.sh >_
# $ sed -n '/width/p;/height/p' _ | sort | uniq

for site in shonenjumpplus comic-days; do
  base="https://${site}.com"
  {
  curl -s "$base"
  curl -s "${base}/series"
  } | grep -oP "${base}/episode/\d+" | sort | uniq |
  while read episode;do
    echo "${episode}.json"
    curl -s "${episode}.json" | grep -oP '("height"|"width"):\d+' |
    sort | uniq
  done
done
