from __future__ import annotations

import json
import os
import re
import sys
import warnings
from io import BytesIO
from typing import TypedDict
from urllib.parse import urlparse

import requests
from PIL import Image

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/67.0.3396.99 Safari/537.36"
    )
}

VALID_HOSTS = (
    "www.corocoro.jp",
    "comic-action.com",
    "comic-days.com",
    "comic-gardo.com",
    "comic-ogyaaa.com",
    "comic-trail.com",
    "comic-zenon.com",
    "comicborder.com",
    "comicbushi-web.com",
    "feelweb.jp",
    "kuragebunch.com",
    "magcomi.com",
    "pocket.shonenmagazine.com",
    "shonenjumpplus.com",
    "www.sunday-webry.com",
    "tonarinoyj.jp",
    "viewer.heros-web.com",
)


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
        self._loggedin_hosts: list[str] = []
        self._session: requests.Session = requests.Session()

    def get(
        self,
        url: str,
        save_path: str = ".",
        overwrite: bool = True,
        only_first: bool = False,
        username: str | None = None,
        password: str | None = None,
        save_metadata: bool = False,
    ) -> tuple[str | None, str, bool]:
        self.__check_url(url)
        self.login(url, username, password)
        url = (
            url
            if url.endswith(".json")
            else re.sub(r"((episode|magazine|volume)/\d+)", r"\1.json", url)
        )
        res = self._session.get(url, headers=HEADERS)
        self.__check_content_type(res.headers["content-type"])
        j = res.json()["readableProduct"]
        nxt = j["nextReadableProductUri"]
        nxt = self.__check_next(nxt)
        if j["typeName"] == "magazine":
            series_title = re.sub(
                r"\s*([0-9０-９]+年)?([0-9０-９]+月?号|(Ｎｏ|ｖｏｌ)．[0-9０-９]+)$", "", j["title"]
            )
        elif j["typeName"] == "episode":
            series_title = j["series"]["title"].replace("/", "／")
        title = j["title"].replace("/", "／")
        # print(f"[series={repr(series_title)}, title={repr(title)}]")

        save_dir = os.path.join(save_path, series_title, title)
        if os.path.exists(save_dir) and not overwrite:
            print("already existed! (to overwrite, use `-o`)", file=sys.stderr)
            return nxt, save_dir, False
        os.makedirs(save_dir, exist_ok=True)

        if not j["isPublic"] and not j["hasPurchased"]:
            warnings.warn(title, NeedPurchase, stacklevel=1)
            print(j["isPublic"], j["hasPurchased"])
            return nxt, save_dir, False
        else:
            pages: list[Page] = [p for p in j["pageStructure"]["pages"] if "src" in p]

        if save_metadata:
            print(
                json.dumps(res.json(), indent=4),
                file=open(os.path.join(save_dir, "metadata.json"), "w"),
            )
        self.__save_images(pages, save_dir, only_first)

        return nxt, save_dir, True

    @staticmethod
    def is_valid_uri(url: str) -> bool:
        o = urlparse(url)
        return (
            type(url) is str
            and o.scheme == "https"
            and o.hostname in VALID_HOSTS
            and bool(re.match(r"^/(episode|magazine|volume)/\d+(\.json)?$", o.path))
        )

    def login(
        self,
        url: str,
        username: str | None = None,
        password: str | None = None,
        overwrite: bool = False,
    ) -> requests.Response | None:
        if username is None and password is None:
            return None  # needless to login
        o = urlparse(url)
        base_url = f"{o.scheme}://{o.netloc}"
        login_url = f"{base_url}/user_account/login"
        if base_url in self._loggedin_hosts and not overwrite:
            return None  # skip if already being loggedin
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
            self._loggedin_hosts.append(base_url)
        else:
            raise ValueError(
                f"Maybe login (to: {login_url}) is failed (code: {status_code}). "
                "Is given information correct?"
            )
        return res

    def __check_url(self, url: str) -> None:
        if not self.is_valid_uri(url):
            raise ValueError(f"'{url}' is not valid url.")

    @staticmethod
    def __check_content_type(type_: str) -> None:
        if "application/json" not in type_:
            raise TypeError(
                f"got '{type_}', expect 'application/json'. Is given URL correct?"
            )

    @staticmethod
    def __check_next(nxt: str | None) -> str | None:
        return nxt + ".json" if type(nxt) is str else nxt

    def __save_images(
        self, pages: list[Page], save_dir: str, only_first: bool = False
    ) -> None:
        imgs: list[Image.Image] = []
        for page in pages:
            img = self.__get_image(page["src"])
            imgs.append(img)
            if only_first:
                break

        len_page_digit = len(str(len(imgs)))
        for idx, img in enumerate(imgs):
            save_img_path = os.path.join(
                save_dir, f"%0{len_page_digit}d" % idx + ".jpg"
            )
            img.save(save_img_path)

    def __get_image(self, image_src: str, div: int = 4, mul: int = 8) -> Image.Image:
        img = Image.open(BytesIO(requests.get(image_src).content))
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
                    )
                )
                inbuff.append(cropped)
            buff.append(inbuff)

        for y, inbuff in enumerate(buff):
            for x, cropped in enumerate(inbuff):
                img.paste(cropped, box=(fixed_width * x, fixed_height * y))
        return img
