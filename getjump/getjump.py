from __future__ import annotations

import os
import re
import sys
import warnings
from typing import Any, cast
from urllib.parse import urlparse

import cv2  # type: ignore[import]
import numpy as np
import numpy.typing as npt
import requests

from .gap import HEIGHT_GAP, WIDTH_GAP

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
            pages = [p for p in j["pageStructure"]["pages"] if "src" in p]

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
                f"Maybe login (to: {login_url}) is failed (code: {status_code}). Is given information correct?"
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
        self, pages: list[Any], save_dir: str, only_first: bool = False
    ) -> None:
        imgs: list[npt.ArrayLike] = []
        for page in pages:
            img = self.__get_image(page)
            imgs.append(img)
            if only_first:
                break

        len_page_digit = len(str(len(imgs)))
        for idx, img in enumerate(imgs):
            save_img_path = os.path.join(
                save_dir, f"%0{len_page_digit}d" % idx + ".jpg"
            )
            self.__imwrite(save_img_path, img)

    @staticmethod
    def __imwrite(filename: str, img: npt.ArrayLike) -> bool:
        _, ext = os.path.splitext(filename)
        result, n = cast(tuple[bool, np.ndarray[Any, Any]], cv2.imencode(ext, img))
        if result:
            with open(filename, mode="w+b") as f:
                n.tofile(f)
            return True
        return False

    def __get_image(self, image_dic: dict[str, Any]) -> npt.ArrayLike:
        src = image_dic["src"]
        img = requests.get(src, stream=True).raw
        img = np.asarray(bytearray(img.read()), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        offset = 4
        height, width = img.shape[:2]
        dice_height = int((height - self.__get_height_gap(height)) / offset)
        dice_width = int((width - self.__get_width_gap(width)) / offset)
        pieces = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        for x in range(offset):
            for y in range(offset):
                x_slice = slice(x * dice_height, (x + 1) * dice_height)
                y_slice = slice(y * dice_width, (y + 1) * dice_width)

                piece = img[x_slice, y_slice]
                pieces[y][x] = piece

        img = cv2.vconcat([cv2.hconcat(x) for x in pieces])
        return cast(npt.ArrayLike, img)

    @staticmethod
    def __get_height_gap(height: int) -> int:
        if height in HEIGHT_GAP:
            if type(HEIGHT_GAP[height]) is not int:
                raise ValueError(
                    "Unresearched height (please let me know with issue <https://git.io/J2jV3>): %d"
                    % height
                )
            else:
                return HEIGHT_GAP[height]
        else:
            raise ValueError(
                "Unfamiliar height (please let me know with issue <https://git.io/J2jV3>): %d"
                % height
            )

    @staticmethod
    def __get_width_gap(width: int) -> int:
        if width in WIDTH_GAP:
            if type(WIDTH_GAP[width]) is not int:
                raise ValueError(
                    "Unresearched width (please let me know with issue <https://git.io/J2jV3>): %d"
                    % width
                )
            else:
                return WIDTH_GAP[width]
        else:
            raise ValueError(
                "Unfamiliar width (please let me know with issue <https://git.io/J2jV3>): %d"
                % width
            )
