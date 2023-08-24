from __future__ import annotations

import argparse
import http.client as httplib
import socket
import sys
from shutil import get_terminal_size

from . import __version__
from .getjump import VALID_HOSTS, GetJump


class GetJumpFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


class HttpConnectionNotFountError(Exception):
    pass


def available_list() -> str:
    return "available urls:\n  - https://" + "\n  - https://".join(VALID_HOSTS)


def check_connectivity(url: str = "www.google.com", timeout: int = 3) -> bool:
    conn = httplib.HTTPConnection(url, timeout=timeout)
    try:
        conn.request("HEAD", "/")
        conn.close()
    except socket.gaierror as e:
        print(e, file=sys.stderr)
        return False
    return True


def check_url(v: str) -> str:
    if GetJump.is_valid_uri(v):
        return v
    raise argparse.ArgumentTypeError(f"'{v}' is invalid.\n" + available_list())


def check_login_info(username: str | None = None, password: str | None = None) -> None:
    if username is None and password is None:
        return
    if username is None:
        raise argparse.ArgumentError(argparse.Action(["-p", "--password"], ""), "Username (-u) is required.")
    if password is None:
        raise argparse.ArgumentError(argparse.Action(["-u", "--username"], ""), "Password (-p) is required.")


def parse_args(test: list[str] | None = None) -> argparse.Namespace:
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        prog="jget",
        formatter_class=(
            lambda prog: GetJumpFormatter(
                prog,
                width=get_terminal_size(fallback=(120, 50)).columns,
                max_help_position=25,
            )
        ),
        description="Get images from jump web viewer",
        epilog=available_list(),
    )

    parser.add_argument(
        "url",
        metavar="url",
        type=check_url,
        help="target url",
    )
    parser.add_argument(
        "-b",
        "--bulk",
        action="store_true",
        help="download series in bulk",
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
        "-f",
        "--first",
        action="store_true",
        help="download only first page",
    )
    parser.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        help="overwrite",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        action="store_true",
        help="save metadata as json",
    )
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        metavar="ID",
        help="username if you want to login",
    )
    parser.add_argument(
        "-p",
        "--password",
        metavar="PW",
        type=str,
        help="password if you want to login",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="disable console print",
    )
    parser.add_argument("-V", "--version", action="version", version=__version__)

    if test:
        return parser.parse_args(test)
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    else:
        return parser.parse_args()


def get_bulk(args: argparse.Namespace) -> None:
    g = GetJump()
    next_uri = args.url
    if not args.quiet:
        print("get:", next_uri)
    while next_uri:
        next_uri, prev_title, ok = g.get(
            next_uri,
            save_path=args.savedir,
            overwrite=args.overwrite,
            only_first=args.first,
            username=args.username,
            password=args.password,
            save_metadata=args.metadata,
            print_log=not args.quiet,
        )
        if not args.quiet:
            if ok:
                print("saved:", prev_title)
            if next_uri is not None:
                print("next:", next_uri)


def get_one(args: argparse.Namespace) -> None:
    g = GetJump()
    next_uri = args.url
    if not args.quiet:
        print("get:", next_uri)
    _, prev_title, ok = g.get(
        next_uri,
        save_path=args.savedir,
        overwrite=args.overwrite,
        only_first=args.first,
        username=args.username,
        password=args.password,
        save_metadata=args.metadata,
        print_log=not args.quiet,
    )
    if ok:
        print("saved:", prev_title)


def main() -> None:
    args = parse_args()
    check_login_info(args.username, args.password)
    if not check_connectivity():
        raise HttpConnectionNotFountError
    if args.bulk:
        get_bulk(args)
    else:
        get_one(args)
    if not args.quiet:
        print("done.")


if __name__ == "__main__":
    main()
