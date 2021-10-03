# getjump

[![PyPI version](https://badge.fury.io/py/getjump.svg)](https://badge.fury.io/py/getjump) [![Maintainability](https://api.codeclimate.com/v1/badges/8d8c16d52b49885dad8c/maintainability)](https://codeclimate.com/github/eggplants/getjump/maintainability)

Get and save images from jump web viewer

*Note: Secondary distribution of downloaded image data is prohibited. Please keep it to private use.*

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
usage: jget [-h] [-d DIR] [-o] [-b] url

Get images from jump web viewer

positional arguments:
  url                   target url (ex:
                        https://shonenjumpplus.com/episode/***.json)

optional arguments:
  -h, --help            show this help message and exit
  -d DIR, --savedir DIR
                        directory to save downloaded images (default: .)
  -o, --overwrite       overwrite or not (default: False)
  -b, --bulk            download series in bulk or not (default: False)
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
