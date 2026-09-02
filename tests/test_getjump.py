from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from getjump import GetJump

if TYPE_CHECKING:
    from pathlib import Path

TEST_URLS: dict[str, str] = {
    "andsofa.com": "https://comic-days.com/episode/13932016480029903802?from=andsofa",
    "comic-action.com": "https://comic-action.com/episode/13933686331621197279",
    "comicbunch-kai.com": "https://kuragebunch.com/episode/2550689798358821780?from=comicbunchkai",
    "comic-days.com": "https://comic-days.com/episode/10834108156631495205",
    "comic-earthstar.com": "https://comic-earthstar.com/episode/14079602755509007065",
    "comic-gardo.com": "https://comic-gardo.com/episode/3269754496561198488",
    "comic-ogyaaa.com": "https://comic-ogyaaa.com/episode/3269754496829572092",
    "comic-seasons.com": "https://comic-seasons.com/episode/2550912964824975149",
    "comic-trail.com": "https://comic-trail.com/episode/3269632237330707078",
    "comic-y-ours.com": "https://comic-y-ours.com/episode/12207421983499079730",
    "comic-zenon.com": "https://comic-zenon.com/episode/10834108156688950516",
    "comicborder.com": "https://comicborder.com/episode/3269632237287061913",
    "feelweb.jp": "https://feelweb.jp/episode/3269754496367124953",
    "ichicomi.com": "https://ichicomi.com/episode/2550912965919401629",
    "kuragebunch.com": "https://kuragebunch.com/episode/3269754496410437550",
    "magcomi.com": "https://magcomi.com/episode/4856001361341293045",
    "mangatime-square.com": "https://mangatime-square.com/episode/12207421983667738694",
    "ourfeel.jp": "https://ourfeel.jp/episode/2550689798581262904",
    "shonenjumpplus.com": "https://shonenjumpplus.com/episode/10834108156648240735",
    "tonarinoyj.jp": "https://tonarinoyj.jp/episode/10834108156765668108",
    "www.sunday-webry.com": "https://www.sunday-webry.com/episode/3269754496551508334",
}


@pytest.mark.parametrize("target", TEST_URLS)
def test_site_download(tmp_path: Path, target: str) -> None:
    g = GetJump()
    _next_uri, _prev_title, saved = g.get(
        TEST_URLS[target],
        save_path=str(tmp_path),
        only_first=True,
    )
    assert saved is True


def test_first_episode_download(tmp_path: Path) -> None:
    g = GetJump()
    _next_uri, _prev_title, saved = g.get(
        "https://comic-days.com/series/2550912964574304403/first_episode",
        save_path=str(tmp_path),
        only_first=True,
    )
    assert saved is True


RSS_URL = "https://shonenjumpplus.com/rss/series/3269632237310729745"


def test_rss_download(tmp_path: Path) -> None:
    g = GetJump()
    urls = g.get_episode_urls(RSS_URL)
    assert len(urls) > 1
    assert all(GetJump.is_valid_uri(url) for url in urls)
    # episodes needing purchase are skipped (`NeedPurchase`), so only require any of them to be saved
    saved_urls = [
        url
        for url in urls
        if g.get(
            url,
            save_path=str(tmp_path),
            only_first=True,
        )[2]
    ]
    assert saved_urls


def test_get_episode_urls_passthrough() -> None:
    g = GetJump()
    url = "https://comic-days.com/episode/2550912964611244527"
    assert g.get_episode_urls(url) == [url]


def test_get_rejects_feed_url(tmp_path: Path) -> None:
    g = GetJump()
    with pytest.raises(ValueError, match="is a feed"):
        g.get(RSS_URL, save_path=str(tmp_path), only_first=True)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://comic-days.com/series/2550912964574304403/first_episode", True),
        ("https://comic-days.com/episode/2550912964611244527", True),
        ("https://shonenjumpplus.com/rss/series/3269632237310729745", True),
        ("https://comic-days.com/series/2550912964574304403", False),
        ("https://comic-days.com/series/first_episode", False),
        ("https://shonenjumpplus.com/rss/series/", False),
        ("https://example.com/series/2550912964574304403/first_episode", False),
    ],
)
def test_is_valid_uri(url: str, expected: bool) -> None:  # noqa: FBT001
    assert GetJump.is_valid_uri(url) is expected
