# getjump

[![PyPI version](https://badge.fury.io/py/getjump.svg)](https://badge.fury.io/py/getjump) [![Maintainability](https://api.codeclimate.com/v1/badges/8d8c16d52b49885dad8c/maintainability)](https://codeclimate.com/github/eggplants/getjump/maintainability)

Retrieve and save images from manga distribution sites using [GigaViewer]()

*Note: Secondary distribution of downloaded image data is prohibited. Please keep it to private use.*

## Available Site

- `https://comic-action.com/episode/***.json`
- `https://comic-days.com/episode/***.json`
- `https://comic-gardo.com/episode/***.json`
- `https://comic-trail.com/episode/***.json`
- `https://comic-zenon.com/episode/***.json`
- `https://comicborder.com/episode/***.json`
- `https://comicbushi-web.com/episode/***.json`
- `https://feelweb.jp/episode/***.json`
- `https://kuragebunch.com/episode/***.json`
- `https://magcomi.com/episode/***.json`
- `https://pocket.shonenmagazine.com/episode/***.json`
- `https://shonenjumpplus.com/episode/***.json`
- `https://tonarinoyj.jp/episode/***.json`
- `https://viewer.heros-web.com/episode/***.json`

## Install

```bash
# Python>=3.9
pip install getjump
```

## Library

```python
import getjump as g

G = g.GetJump()
next_uri = "https://shonenjumpplus.com/episode/13932016480028799982.json"
while next_uri:
    next_uri, prev_title = G.get(next_uri, overwrite=False)
    print("saved:", prev_title)
    print("next:", next_uri)
```

## CLI

```shellsession
$ jget -h
usage: jget [-h] [-b] [-d DIR] [-f] [-o] url

Get images from jump web viewer

positional arguments:
  url                   target url

optional arguments:
  -h, --help            show this help message and exit
  -b, --bulk            download series in bulk (default: False)
  -d DIR, --savedir DIR
                        directory to save downloaded images (default: .)
  -f, --first           download only first page (default: False)
  -o, --overwrite       overwrite (default: False)
$ jget https://shonenjumpplus.com/episode/13932016480028799982.json
saved: ./阿波連さんははかれない/[1話]阿波連さんははかれない
$ jget -b https://shonenjumpplus.com/episode/10833519556325021912.json
saved: ./こちら葛飾区亀有公園前派出所/[第1話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/10833519556325022016.json
saved: ./こちら葛飾区亀有公園前派出所/[第2話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/10833519556325022128.json
saved: ./こちら葛飾区亀有公園前派出所/[第3話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/10833519556325022500.json
...
saved: ./こちら葛飾区亀有公園前派出所/[第1950話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/13932016480028744844.json
saved: ./こちら葛飾区亀有公園前派出所/[第1951話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/13932016480028744845.json
saved: ./こちら葛飾区亀有公園前派出所/[第1952話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/13932016480028744846.json
saved: ./こちら葛飾区亀有公園前派出所/[第1953話]こちら葛飾区亀有公園前派出所
next: None
$
```

## License

MIT

## Reference

- [fa0311/jump-downloader](https://github.com/fa0311/jump-downloader)
- [少年ジャンププラスの漫画をダウンロードするライブラリ - yuki0311.com](https://blog.yuki0311.com/jumppuls_downloader/)
- [はてな開発の新マンガビューワを「少年ジャンプ＋」が採用。集英社と共同でサイト成長、マネタイズの両面を加速 - プレスリリース - 株式会社はてな](https://hatenacorp.jp/press/release/entry/2017/01/18/113000)
- [はてな、集英社「少年ジャンプ＋」ブラウザ版への機能提供を拡張。ブラウザ版への電子版「週刊少年ジャンプ」定期購読が可能に｜株式会社はてなのプレスリリース](https://prtimes.jp/main/html/rd/p/000000078.000006510.html)
- [GigaViewer の検索結果 - プレスリリース - 株式会社はてな](https://hatenacorp.jp/press/release/search?q=GigaViewer)
- [GigaViewer（ギガビューワー）を作るにあたって - daily thinking running](https://jusei.hatenablog.com/entry/2018/01/09/172026)
