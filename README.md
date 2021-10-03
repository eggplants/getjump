# jumpget

Get and save images from jump web viewer.

## Library

```python
from getjump import GetJump as gj

next_uri = "https://shonenjumpplus.com/episode/13932016480028799982.json"
while next_uri:
    next_uri, prev_title = g.get(next_uri, overwrite=False)
    print("saved:", prev_title)
    print("next:", next_uri)
```

## CLI

```shellsession
$ jget -h
usage: jget [-h] [-d SAVEDIR] [-o] [-b] url

Get images from jump web viewer

positional arguments:
  url                   target url (ex: https://shonenjumpplus.com/episode/***.json)

optional arguments:
  -h, --help            show this help message and exit
  -d SAVEDIR, --savedir SAVEDIR
                        directory to save downloaded images
  -o, --overwrite       overwrite or not
  -b, --bulk            download in bulk or not
$ jget https://shonenjumpplus.com/episode/13932016480028799982.json
saved: ./阿波連さんははかれない/[1話]阿波連さんははかれない
```

## License

MIT


## Reference

- [fa0311/jump-downloader](https://github.com/fa0311/jump-downloader)
- [少年ジャンププラスの漫画をダウンロードするライブラリ - yuki0311.com](https://blog.yuki0311.com/jumppuls_downloader/)
