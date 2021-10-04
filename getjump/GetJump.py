import os
import warnings
from typing import Any

import cv2
import numpy as np
import numpy.typing as npt
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/67.0.3396.99 Safari/537.36"
    )
}

HEIGHT_GAP = {
    448: None,
    472: None,
    480: None,
    584: None,
    626: None,
    670: None,
    700: None,
    774: None,
    798: None,
    954: None,
    960: None,
    1000: 6,
    1024: 0,
    1122: None,
    1154: None,
    1161: None,
    1163: None,
    1195: None,
    1200: 16,
    1400: None,
    1489: None,
    1600: 0,
    1603: None,
    1687: None,
    1811: 16,
    1826: 0,
    2000: 16,
    2048: 0,
    2062: None,
    2100: None,
}

WIDTH_GAP = {
    332: None,
    426: None,
    438: None,
    475: None,
    575: None,
    656: None,  # ########
    658: None,
    667: None,  # ########
    690: 16,
    698: None,
    704: 0,
    712: None,  # #######
    720: 15,
    760: 24,
    764: 25,
    820: 20,
    822: 22,
    836: 4,
    840: None,
    844: 10,
    958: None,
    980: None,
    1042: None,  # ####
    1070: None,  # ######
    1073: None,
    1093: None,
    1114: 23,
    1115: None,  # #####
    1120: None,  # #
    1121: 0,
    1125: 2,
    1127: 5,
    1128: 6,
    1326: 12,
    1394: None,
    1408: None,
    1440: None,  # ########
    1441: None,  # top
    1443: None,  # ##
    1444: None,  # ###
    1453: None,
    1480: None,
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
    ) -> tuple[str, str]:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            raise ConnectionError(r.status_code)
        j = r.json()["readableProduct"]
        next = j["nextReadableProductUri"]
        next = next + ".json" if type(next) is str else next
        series_title = j["series"]["title"]
        title = j["title"]

        save_dir = os.path.join(save_path, series_title, title)
        if os.path.exists(save_dir) and not overwrite:
            return next, save_dir
        os.makedirs(save_dir, exist_ok=True)

        if not j["isPublic"] and not j["hasPurchased"]:
            warnings.warn(title, NeedPurchase, stacklevel=1)
            return next, save_dir
        else:
            pages = j["pageStructure"]["pages"]

        self.__save_images(pages, save_dir, only_first)

        return next, save_dir

    def __save_images(
        self, pages: list[Any], save_dir: str, only_first: bool = False
    ) -> None:
        imgs = []
        for page in pages:
            if "src" not in page:
                continue
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
                return HEIGHT_GAP[height]  # type: ignore
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
                return WIDTH_GAP[width]  # type: ignore
        else:
            raise ValueError(
                "Unfamiliar width (please let me know with issue <https://git.io/J2jV3>): %d"
                % width
            )


def main() -> None:
    g = GetJump()
    next_uri = "https://shonenjumpplus.com/episode/13932016480028799982.json"
    while next_uri:
        next_uri, prev_title = g.get(next_uri, overwrite=False)
        print("saved:", prev_title)
        print("next:", next_uri)


if __name__ == "__main__":
    main()
