import os
import re
import sys
import warnings
from typing import Any, Optional, cast

import cv2
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


class NeedPurchase(Warning):
    pass


class GetJump:
    def __init__(self) -> None:
        pass

    def get(
        self,
        url: str,
        save_path: str = ".",
        overwrite: bool = True,
        only_first: bool = False,
    ) -> tuple[Optional[str], str, bool]:
        self.__check_url(url)
        r = requests.get(url, headers=HEADERS)
        self.__check_content_type(r.headers["content-type"])
        j = r.json()["readableProduct"]
        nxt = j["nextReadableProductUri"]
        nxt = self.__check_next(nxt)
        series_title = j["series"]["title"].replace("/", "／")
        title = j["title"].replace("/", "／")

        save_dir = os.path.join(save_path, series_title, title)
        if os.path.exists(save_dir) and not overwrite:
            print("already existed! (to overwrite, use `-o`)", file=sys.stderr)
            return nxt, save_dir, False
        os.makedirs(save_dir, exist_ok=True)

        if not j["isPublic"] and not j["hasPurchased"]:
            warnings.warn(title, NeedPurchase, stacklevel=1)
            return nxt, save_dir, False
        else:
            pages = [p for p in j["pageStructure"]["pages"] if "src" in p]

        self.__save_images(pages, save_dir, only_first)

        return nxt, save_dir, True

    @staticmethod
    def is_valid_uri(url: str) -> bool:
        pattern = re.compile(
            r"""
            ^https://(?:pocket\.shonenmagazine\.com
            |(?:(?:viewer\.heros\-web|shonenjumpplus|comicbushi\-web
            |comic(?:\-(?:action|gardo|trail|zenon)|border)
            |kuragebunch|comic\-days|magcomi)\.com
            |(?:tonarinoyj|feelweb)\.jp))/episode/\d+.json$
            """,
            re.X,
        )
        return type(url) is str and bool(pattern.match(url))

    def __check_url(self, url: str) -> None:
        if not self.is_valid_uri(url):
            raise ValueError("'{}' is not valid url.".format(url))

    @staticmethod
    def __check_content_type(type_: str) -> None:
        if "application/json" not in type_:
            raise TypeError(type_ + " is not application/json")

    @staticmethod
    def __check_next(nxt: Optional[str]) -> Optional[str]:
        return nxt + ".json" if type(nxt) is str else nxt

    def __save_images(
        self, pages: list[Any], save_dir: str, only_first: bool = False
    ) -> None:
        imgs = []
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
            cv2.imwrite(save_img_path, img)

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
        return img

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
