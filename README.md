# getjump

[![PyPI version](
  <https://badge.fury.io/py/getjump.svg>
  )](
  <https://badge.fury.io/py/getjump>
) [![Maintainability](
  <https://qlty.sh/badges/030f45a4-2fa5-4268-be52-41a7205c35d3/maintainability.svg>
  )](
  <https://qlty.sh/gh/eggplants/projects/getjump>
) [![pre-commit.ci status](
  <https://results.pre-commit.ci/badge/github/eggplants/getjump/master.svg>
  )](
  <https://results.pre-commit.ci/latest/github/eggplants/getjump/master>
) [![Code Coverage](
  <https://qlty.sh/badges/030f45a4-2fa5-4268-be52-41a7205c35d3/test_coverage.svg>
  )](
  <https://qlty.sh/gh/eggplants/projects/getjump>
) [![Test](
  <https://github.com/eggplants/getjump/actions/workflows/test.yml/badge.svg>
  )](
  <https://github.com/eggplants/getjump/actions/workflows/test.yml>
)

[![ghcr latest](
  <https://ghcr-badge.egpl.dev/eggplants/getjump/latest_tag?trim=major&label=latest>
 ) ![ghcr size](
  <https://ghcr-badge.egpl.dev/eggplants/getjump/size>
)](
  <https://github.com/eggplants/getjump/pkgs/container/getjump>
)

- Retrieve and save images from manga distribution sites using [GigaViewer](https://hatena.co.jp/solutions/gigaviewer)
  - If you read retrieved comics as combined PDF, use: [eggplants/mkbook](https://github.com/eggplants/mkbook)

_Note: Redistribution of downloaded image data is prohibited. Please keep it to private use._

## Screenshot

![image](https://user-images.githubusercontent.com/42153744/175097993-c6a2e162-50ea-41d4-9590-19a09a61e053.png)

## Valid URL Formats

- `<host>/(episode|magazine|volume)/<number>`
  - e.g. <https://shonenjumpplus.com/episode/13932016480028799982>

## Available Hosts

- `https://comic-action.com`
- `https://comic-days.com`
- `https://comic-earthstar.com`
- `https://comic-gardo.com`
- `https://comic-ogyaaa.com`
- `https://comic-seasons.com`
- `https://comic-trail.com`
- `https://comic-zenon.com`
- `https://comicborder.com`
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
$ jget -b https://kuragebunch.com/episode/10834108156628843815
get: https://kuragebunch.com/episode/10834108156628843815
  Downloading... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% ( 18/18 pages ) remain: 0:00:00 spent: 0:00:02
  Saving...      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% ( 18/18 pages ) remain: 0:00:00 spent: 0:00:00
saved: 少女終末旅行/01 星空
next: https://kuragebunch.com/episode/10834108156628843819
...
saved: 少女終末旅行/42 終末
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
  - https://comic-seasons.com
  - https://comic-trail.com
  - https://comic-zenon.com
  - https://comicborder.com
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
