from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from getjump import GetJump

if TYPE_CHECKING:
    from pathlib import Path

GET = GetJump().get
TEST_URLS: dict[str, str] = {
    "andsofa.com": "https://comic-days.com/episode/13932016480029903802?from=andsofa",
    "www.corocoro.jp": "https://www.corocoro.jp/episode/3269754496804969156",
    "comic-action.com": "https://comic-action.com/episode/13933686331621197279",
    "comic-days.com": "https://comic-days.com/episode/10834108156631495205",
    "comic-gardo.com": "https://comic-gardo.com/episode/3269754496561198488",
    "comic-ogyaaa.com": "https://comic-ogyaaa.com/episode/3269754496829572092",
    "comic-trail.com": "https://comic-trail.com/episode/3269632237330707078",
    "comic-zenon.com": "https://comic-zenon.com/episode/10834108156688950516",
    "comicborder.com": "https://comicborder.com/episode/3269632237287061913",
    "comicbushi-web.com": "https://comicbushi-web.com/episode/13933686331793879490",
    "feelweb.jp": "https://feelweb.jp/episode/3269754496367124953",
    "kuragebunch.com": "https://kuragebunch.com/episode/3269754496410437550",
    "magcomi.com": "https://magcomi.com/episode/10834108156763618369",
    "pocket.shonenmagazine.com": "https://pocket.shonenmagazine.com/episode/13932016480029113171",
    "shonenjumpplus.com": "https://shonenjumpplus.com/episode/10834108156648240735",
    "tonarinoyj.jp": "https://tonarinoyj.jp/episode/10834108156765668108",
    "viewer.heros-web.com": "https://viewer.heros-web.com/episode/10834108156713782929",
    "www.sunday-webry.com": "https://www.sunday-webry.com/episode/3269754496551508334",
}


@pytest.mark.parametrize("target_page", TEST_URLS.values())
def test_site_download(tmp_path: Path, target_page: str) -> None:
    _next_uri, _prev_title, saved = GET(target_page, save_path=str(tmp_path), only_first=True)
    assert saved is True
