from __future__ import annotations

import json
import re
import sys
import warnings
from io import BytesIO
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from PIL import Image
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/67.0.3396.99 Safari/537.36"
    ),
}

VALID_HOSTS = (
    "comic-action.com",
    "comic-days.com",
    "comic-earthstar.com",
    "comic-gardo.com",
    "comic-ogyaaa.com",
    "comic-trail.com",
    "comic-zenon.com",
    "comicborder.com",
    "comic-growl.com",
    "feelweb.jp",
    "kuragebunch.com",
    "magcomi.com",
    "ourfeel.jp",
    "pocket.shonenmagazine.com",
    "shonenjumpplus.com",
    "www.sunday-webry.com",
    "tonarinoyj.jp",
    "viewer.heros-web.com",
)

# https://regex101.com/r/j0nUsd/1
_MAGAZINE_TITLE_PATTERN = r"([0-90-9]+年)?([0-90-9]+?(・?[0-90-9]+(合併)?)?月?号|(No|vol).[0-90-9]+)$"


class _Page(TypedDict):
    height: int
    src: str
    type: str
    width: int


class Page(_Page, total=False):
    contentBegin: str
    contentEnd: str


class NeedPurchase(Warning):
    pass


class GetJump:
    def __init__(self) -> None:
        self._logged_in_hosts: list[str] = []
        self._session: requests.Session = requests.Session()

    def get(  # noqa: PLR0913
        self,
        url: str,
        save_path: str | Path = ".",
        *,
        overwrite: bool = True,
        only_first: bool = False,
        username: str | None = None,
        password: str | None = None,
        save_metadata: bool = False,
        print_log: bool = False,
    ) -> tuple[str | None, Path, bool]:
        self.__check_url(url)
        self.login(url, username=username, password=password)

        url = url[:-5] if url.endswith(".json") else url

        res = self._session.get(url, headers=HEADERS)
        self.__check_content_type(res.headers["content-type"])

        script_tag = BeautifulSoup(res.content, "html.parser").find("script", id="episode-json")
        if not isinstance(script_tag, Tag):
            msg = "wrong type of script element."
            raise TypeError(msg)

        json_value = script_tag.attrs.get("data-value", None)
        if json_value is None:
            msg = "json data is missing."
            raise ValueError(msg)

        j = json.loads(json_value)["readableProduct"]

        nxt = j["nextReadableProductUri"]
        nxt = self.__check_next(nxt)

        if j["typeName"] == "magazine":
            series_title = self.__get_series_title(url, j["title"])
            title = j["title"].replace(series_title, "")
        elif j["typeName"] == "episode" or "volume":
            series_title = j["series"]["title"].replace("/", "/")
            title = j["title"].replace("/", "/")
        else:
            msg = f"Unknown typeName: {j['typeName']}"
            raise ValueError(msg)

        series_title = self.__normalize_fname(series_title)
        title = self.__normalize_fname(title)

        save_dir = Path(save_path) / series_title / title
        if save_dir.exists() and not overwrite:
            if print_log:
                print("already existed! (to overwrite, use `-o`)", file=sys.stderr)  # noqa: T201
            return nxt, save_dir, False
        save_dir.mkdir(exist_ok=True, parents=True)

        if not j["isPublic"] and not j["hasPurchased"]:
            warnings.warn(title, NeedPurchase, stacklevel=1)
            if print_log:
                print(j["isPublic"], j["hasPurchased"])  # noqa: T201
            return nxt, save_dir, False
        pages: list[Page] = [p for p in j["pageStructure"]["pages"] if "src" in p]

        if save_metadata:
            print(
                json.dumps(json.loads(json_value), indent=4, ensure_ascii=False),
                file=(save_dir / "metadata.json").open(mode="w"),
            )
        self.__save_images(pages, save_dir, only_first=only_first, print_log=print_log)

        return nxt, save_dir, True

    @staticmethod
    def is_valid_uri(url: str) -> bool:
        o = urlparse(url)
        return (
            o.scheme == "https"
            and o.hostname in VALID_HOSTS
            and bool(re.match(r"^/(episode|magazine|volume)/\d+(\.json)?$", o.path))
        )

    def login(
        self,
        url: str,
        *,
        username: str | None = None,
        password: str | None = None,
        overwrite: bool = False,
    ) -> requests.Response | None:
        if username is None and password is None:
            return None  # needless to login
        o = urlparse(url)
        base_url = f"{o.scheme}://{o.netloc}"
        login_url = f"{base_url}/user_account/login"
        if base_url in self._logged_in_hosts and not overwrite:
            return None  # skip if already being logged in
        res = self._session.post(
            login_url,
            data={
                "email_address": username,
                "password": password,
                "return_location_path": url,
            },
            headers={
                "User-Agent": HEADERS["User-Agent"],
                "x-requested-with": "XMLHttpRequest",
            },
        )
        status_code = res.status_code
        if res.ok:
            self._logged_in_hosts.append(base_url)
        else:
            msg = f"Maybe login (to: {login_url}) is failed (code: {status_code}). Is given information correct?"
            raise ValueError(msg)
        return res

    def __check_url(self, url: str) -> None:
        if not self.is_valid_uri(url):
            msg = f"'{url}' is not valid url."
            raise ValueError(msg)

    @staticmethod
    def __check_content_type(type_: str) -> None:
        if "text/html" not in type_:
            msg = f"got '{type_}', expect 'text/html'. Is given URL correct?"
            raise TypeError(msg)

    @staticmethod
    def __check_next(nxt: str | None) -> str | None:
        return nxt + ".json" if isinstance(nxt, str) else nxt

    def __save_images(
        self,
        pages: list[Page],
        save_dir: Path,
        *,
        only_first: bool = False,
        print_log: bool = False,
    ) -> None:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("("),
            MofNCompleteColumn(),
            TextColumn("pages"),
            TextColumn(")"),
            TextColumn("remain:"),
            TimeRemainingColumn(),
            TextColumn("spent:"),
            TimeElapsedColumn(),
            disable=not print_log,
        )
        with progress:
            imgs: list[Image.Image] = []
            task_dl = progress.add_task("[red]Downloading...", total=1 if only_first else len(pages))
            for page in pages:
                img = self.__get_image(page["src"])
                imgs.append(img)
                progress.update(task_dl, advance=1)
                if only_first:
                    break

            len_page_digit = len(str(len(imgs)))
            task_save = progress.add_task("[green]Saving...", total=len(imgs))
            for idx, img in enumerate(imgs):
                save_img_name = f"%0{len_page_digit}d" % idx
                save_img_path = Path(save_dir) / save_img_name
                img.save(save_img_path.with_suffix(".jpg"))
                progress.update(task_save, advance=1)

    def __get_image(self, image_src: str, div: int = 4, mul: int = 8) -> Image.Image:
        img = Image.open(BytesIO(requests.get(image_src, timeout=10).content))
        img_width, img_height = img.size
        fixed_width = int(float(img_width) / (div * mul)) * mul
        fixed_height = int(float(img_height) / (div * mul)) * mul
        buff: list[list[Image.Image]] = []
        for x in range(div):
            inbuff: list[Image.Image] = []
            for y in range(div):
                cropped = img.crop(
                    box=(
                        fixed_width * x,
                        fixed_height * y,
                        fixed_width * (x + 1),
                        fixed_height * (y + 1),
                    ),
                )
                inbuff.append(cropped)
            buff.append(inbuff)

        for y, inbuff in enumerate(buff):
            for x, cropped in enumerate(inbuff):
                img.paste(cropped, box=(fixed_width * x, fixed_height * y))
        return img

    def __normalize_fname(self, fname: str) -> str:
        if not fname:
            msg = f"{fname!r} is empty."
            raise ValueError(msg)
        if fname.endswith("."):
            return self.__normalize_fname(fname[:-1])
        if fname.startswith(" "):
            return self.__normalize_fname(fname[1:])
        if fname.endswith(" "):
            return self.__normalize_fname(fname[:-1])
        return fname

    def __get_series_title(self, url: str, title: str) -> str:
        res = self._session.get(url.replace(".json", ""), headers=HEADERS)
        title_tag = BeautifulSoup(res.content, "html.parser").find("h1", class_="series-header-title")
        if title_tag is None:
            return re.sub(r"\s*" + _MAGAZINE_TITLE_PATTERN, "", title)

        return title_tag.text
