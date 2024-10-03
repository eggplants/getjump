# getjump

[![PyPI version](
  <https://badge.fury.io/py/getjump.svg>
  )](
  <https://badge.fury.io/py/getjump>
) [![Maintainability](
  <https://api.codeclimate.com/v1/badges/8d8c16d52b49885dad8c/maintainability>
  )](
  <https://codeclimate.com/github/eggplants/getjump/maintainability>
) [![pre-commit.ci status](
  <https://results.pre-commit.ci/badge/github/eggplants/getjump/master.svg>
  )](
  <https://results.pre-commit.ci/latest/github/eggplants/getjump/master>
) [![Test Coverage](
  <https://api.codeclimate.com/v1/badges/8d8c16d52b49885dad8c/test_coverage>
  )](
  <https://codeclimate.com/github/eggplants/getjump/test_coverage>
) [![Test](
  <https://github.com/eggplants/getjump/actions/workflows/test.yml/badge.svg>
  )](
  <https://github.com/eggplants/getjump/actions/workflows/test.yml>
)

[![ghcr latest](
  <https://ghcr-badge.deta.dev/eggplants/getjump/latest_tag?trim=major&label=latest>
 ) ![ghcr size](
  <https://ghcr-badge.deta.dev/eggplants/getjump/size>
)](
  <https://github.com/eggplants/getjump/pkgs/container/getjump>
)

- Retrieve and save images from manga distribution sites using [GigaViewer](https://hatena.co.jp/solutions/gigaviewer)
  - If you read retrieved comics as conbined PDF, use: [eggplants/mkbook](https://github.com/eggplants/mkbook)

_Note: Redistribution of downloaded image data is prohibited. Please keep it to private use._

## Screenshot

![image](https://user-images.githubusercontent.com/42153744/175097993-c6a2e162-50ea-41d4-9590-19a09a61e053.png)

## Valid URL Formats

- `<host>/(episode|magazine|volume)/<number>`
  - e.g. <https://shonenjumpplus.com/episode/13932016480028799982>
- `<host>/(episode|magazine|volume)/<number>.json`
  - e.g. <https://shonenjumpplus.com/episode/13932016480028799982.json>

## Available Hosts

- `https://comic-action.com`
- `https://comic-days.com`
- `https://comic-earthstar.com`
- `https://comic-gardo.com`
- `https://comic-ogyaaa.com`
- `https://comic-trail.com`
- `https://comic-zenon.com`
- `https://comicborder.com`
- `https://comic-growl.com`
- `https://feelweb.jp`
- `https://kuragebunch.com`
- `https://magcomi.com`
- `https://ourfeel.jp`
- `https://pocket.shonenmagazine.com`
- `https://shonenjumpplus.com`
- `https://tonarinoyj.jp`
- `https://viewer.heros-web.com`
- `https://www.sunday-webry.com`

## Install

```bash
pip install getjump
```

## CLI

### Usage

```shellsession
$ jget https://shonenjumpplus.com/episode/13932016480028799982.json
get: https://shonenjumpplus.com/episode/13932016480028799982.json
...
saved: ./阿波連さんははかれない/[1話]阿波連さんははかれない
done.

$ jget -b https://shonenjumpplus.com/episode/10833519556325021912.json
get: https://shonenjumpplus.com/episode/10833519556325021912.json
...
saved: ./こちら葛飾区亀有公園前派出所/[第1話]こちら葛飾区亀有公園前派出所
next: https://shonenjumpplus.com/episode/10833519556325022016.json
...
...
...
saved: ./こちら葛飾区亀有公園前派出所/[第1953話]こちら葛飾区亀有公園前派出所
done.
```

### Help

```shellsession
$ jget -h
usage: jget [-h] [-b] [-d DIR] [-f] [-o] [-m] [-u ID] [-p PW] [-q] [-V] url

Get images from jump web viewer

positional arguments:
  url                    target url

options:
  -h, --help             show this help message and exit
  -b, --bulk             download series in bulk (default: False)
  -d DIR, --savedir DIR  directory to save downloaded images (default: .)
  -f, --first            download only first page (default: False)
  -o, --overwrite        overwrite (default: False)
  -m, --metadata         save metadata as json (default: False)
  -u ID, --username ID   username if you want to login (default: None)
  -p PW, --password PW   password if you want to login (default: None)
  -q, --quiet            disable console print (default: False)
  -V, --version          show program's version number and exit

available urls:
  - https://comic-action.com
  - https://comic-days.com
  - https://comic-earthstar.com
  - https://comic-gardo.com
  - https://comic-ogyaaa.com
  - https://comic-trail.com
  - https://comic-zenon.com
  - https://comicborder.com
  - https://comic-growl.com
  - https://feelweb.jp
  - https://kuragebunch.com
  - https://magcomi.com
  - https://ourfeel.jp
  - https://pocket.shonenmagazine.com
  - https://shonenjumpplus.com
  - https://www.sunday-webry.com
  - https://tonarinoyj.jp
  - https://viewer.heros-web.com
```

## Library

### Overview

```python
from getjump import GetJump
g = GetJump()  # create session

g.get(
    url: str,
    save_path: str = ".",
    overwrite: bool = True,
    only_first: bool = False,
    username: str | None = None,
    password: str | None = None,
)
# >>> (next_uri: str | None, prev_title: str, saved: bool)

g.login(
    url: str,
    username: str | None = None,
    password: str | None = None,
    overwrite: bool = False,
)
# >>> logined_response: requests.Response | None

g.is_valid_uri(url: str)
# >>> is_valid_uri: bool
```

### Download all series

To download all series at once:

```python
from getjump import GetJump as g

G = g()
next_uri = "https://shonenjumpplus.com/episode/13932016480028799982.json"
while next_uri:
    next_uri, prev_title, saved = G.get(next_uri, overwrite=False)
    if saved:
        print("saved:", prev_title)
    print("next:", next_uri)
```

### Login

To get purchased or login-required works:

```python
from getjump import GetJump as g

G = g()
G.login("https://shonenjumpplus.com", username="***", password="***")
G.login("https://comic-days.com", username="***", password="***")
...
G.get(...)
```

## License

MIT

---

## Reference

- [fa0311/jump-downloader](https://github.com/fa0311/jump-downloader)
- [少年ジャンププラスの漫画をダウンロードするライブラリ - yuki0311.com](https://blog.yuki0311.com/jumppuls_downloader/)
- [はてな開発の新マンガビューワを「少年ジャンプ＋」が採用。集英社と共同でサイト成長、マネタイズの両面を加速 - プレスリリース - 株式会社はてな](https://hatenacorp.jp/press/release/entry/2017/01/18/113000)
- [はてな、集英社「少年ジャンプ＋」ブラウザ版への機能提供を拡張。ブラウザ版への電子版「週刊少年ジャンプ」定期購読が可能に｜株式会社はてなのプレスリリース](https://prtimes.jp/main/html/rd/p/000000078.000006510.html)
- [GigaViewer の検索結果 - プレスリリース - 株式会社はてな](https://hatenacorp.jp/press/release/search?q=GigaViewer)
- [GigaViewer（ギガビューワー）を作るにあたって - daily thinking running](https://jusei.hatenablog.com/entry/2018/01/09/172026)
