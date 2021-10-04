#!/usr/bin/env bash

links=(
  https://shonenjumpplus.com
  https://shonenjumpplus.com/series
  https://shonenjumpplus.com/series/finished
  https://shonenjumpplus.com/series/oneshot
  https://comic-days.com
  https://comic-days.com/series
  https://comic-days.com/oneshot
  https://comic-days.com/newcomer
)

for link in "${links[@]}"; do
  curl -s "$link"
done |
  grep -oP "https://[a-z\-]+\.com/episode/\d+" | sort | uniq |
  while read -r episode; do
    echo "$episode" >&2
    echo "${episode}.json"
    curl -s "${episode}.json" |
      grep -oP '("height"|"width"):\d+' |
      sort | uniq
  done > episodes

sed -n '/width/p;/height/p' episodes |
  sort | uniq | sort -V > all_size
sed -n '/width/p' episodes |
  sort | uniq -c | sort -rnk1 > width_rank
sed -n '/height/p' episodes |
  sort | uniq -c | sort -rnk1 > height_rank
