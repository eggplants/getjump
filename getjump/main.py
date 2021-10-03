import argparse
import http.client as httplib
import sys
from typing import Optional

from .GetJump import GetJump


class HttpConnectionNotFountError(Exception):
    pass


def check_connectivity(url: str = "www.google.com", timeout: int = 3) -> bool:
    conn = httplib.HTTPConnection(url, timeout=timeout)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except Exception as e:
        print(e, file=sys.stderr)
        return False


def parse_args(test: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="jget",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Get images from jump web viewer",
    )

    parser.add_argument(
        "url",
        metavar="url",
        type=str,
        help="target url (ex: https://shonenjumpplus.com/episode/***.json)",
    )
    parser.add_argument(
        "-d",
        "--savedir",
        type=str,
        metavar="DIR",
        default=".",
        help="directory to save downloaded images",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite or not",
    )
    parser.add_argument(
        "-b",
        "--bulk",
        action="store_true",
        help="download series in bulk or not",
    )

    if test:
        return parser.parse_args(test)
    else:
        return parser.parse_args()


def main() -> None:
    if not check_connectivity():
        raise HttpConnectionNotFountError
    args = parse_args()
    g = GetJump()
    next_uri = args.url
    if args.bulk:
        while next_uri:
            next_uri, prev_title = g.get(
                next_uri, save_path=args.savedir, overwrite=args.overwrite
            )
            print("saved:", prev_title)
            print("next:", next_uri)
    else:
        next_uri, prev_title = g.get(
            next_uri, save_path=args.savedir, overwrite=args.overwrite
        )
        print("saved:", prev_title)


if __name__ == "__main__":
    main()
