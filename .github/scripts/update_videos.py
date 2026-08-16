#!/usr/bin/env python3
"""チャンネルのRSSを読んで index.html の VIDEOS 欄を書き換える。

GitHub Actions から日次で実行される。APIキーは不要（公開RSSのみ）。
index.html の <!-- VIDEOS:AUTO --> 〜 <!-- /VIDEOS:AUTO --> の間だけを置き換える。

  python3 .github/scripts/update_videos.py [--check]

  --check … 書き込まずに差分の有無だけ表示する
"""

from __future__ import annotations

import html
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "index.html"

CHANNEL_ID = "UCXY1m77AzKGFV09ucXD6vxA"  # @Umes-House
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
COUNT = 3  # 掲載する本数（グリッドが3列なので3の倍数にする）

BEGIN = "<!-- VIDEOS:AUTO -->"
END = "<!-- /VIDEOS:AUTO -->"

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
      "Accept-Language": "ja-JP,ja;q=0.9"}


def fetch(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def latest_videos(limit: int) -> list[dict]:
    """RSSから最新動画を取り出す。ショートも混ざるが、RSSでは判別できないのでそのまま扱う。"""
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    root = ET.fromstring(fetch(FEED))
    out = []
    for e in root.findall("a:entry", ns)[:limit]:
        vid = e.find("yt:videoId", ns)
        title = e.find("a:title", ns)
        if vid is None or title is None or not vid.text:
            continue
        out.append({"id": vid.text, "title": (title.text or "").strip()})
    return out


def duration(video_id: str) -> str:
    """動画ページから再生時間を拾う。取れなければ空（その場合は表示しない）。

    RSSに再生時間が無いための補完。YouTube側の仕様変更やアクセス制限で
    取れなくても、動画カード自体は出せるようにしてある。
    """
    try:
        page = fetch(f"https://www.youtube.com/watch?v={video_id}", timeout=20)
    except (urllib.error.URLError, TimeoutError):
        return ""
    m = re.search(r'"lengthSeconds":"(\d+)"', page)
    if not m:
        return ""
    sec = int(m.group(1))
    h, rem = divmod(sec, 3600)
    mi, s = divmod(rem, 60)
    return f"{h}:{mi:02d}:{s:02d}" if h else f"{mi}:{s:02d}"


def existing_durations(src: str) -> dict[str, str]:
    """既に書かれているカードから 動画ID → 再生時間 を拾う。

    Actions の実行環境からは YouTube の動画ページを取れないことがあるため、
    取得に失敗したら前回の値を引き継いで、表示が出たり消えたりしないようにする。
    """
    out = {}
    for m in re.finditer(r'<a class="video.*?watch\?v=([\w-]+)".*?</a>', src, re.S):
        d = re.search(r'<span class="dur">([^<]+)</span>', m.group(0))
        if d:
            out[m.group(1)] = d.group(1)
    return out


def card(v: dict, i: int, known: dict[str, str]) -> str:
    t = html.escape(v["title"], quote=True)
    dur = duration(v["id"]) or known.get(v["id"], "")
    dur_tag = f'\n          <span class="dur">{dur}</span>' if dur else ""
    return f"""      <a class="video rv d{i}" href="https://www.youtube.com/watch?v={v['id']}" target="_blank" rel="noopener">
        <div class="thumb">
          <span class="rec">REC</span>
          <img src="https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg" alt="{t}" loading="lazy">{dur_tag}
          <span class="play"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>
        </div>
        <div class="fbody"><h3>{t}</h3></div>
      </a>"""


def main() -> int:
    check_only = "--check" in sys.argv

    videos = latest_videos(COUNT)
    if len(videos) < COUNT:
        print(f"RSSから{COUNT}本取れなかった（{len(videos)}本）。index.html は変更しない。", file=sys.stderr)
        return 1

    src = INDEX.read_text(encoding="utf-8")
    if BEGIN not in src or END not in src:
        print("index.html に VIDEOS:AUTO マーカーが無い。", file=sys.stderr)
        return 1

    known = existing_durations(src)
    body = "\n".join(card(v, i, known) for i, v in enumerate(videos, start=1))
    # マーカー行のコメント（手書き禁止の注意書き）は残す
    head = src.split(BEGIN, 1)[0] + BEGIN
    note = src.split(BEGIN, 1)[1].split("-->", 1)
    keep = note[0] + "-->" if note[0].lstrip().startswith("<!--") else ""
    tail = END + src.split(END, 1)[1]
    new = f"{head}{keep}\n{body}\n      {tail}"

    if new == src:
        print("変更なし")
        return 0

    print(f"更新あり: {' / '.join(v['title'][:28] for v in videos)}")
    if not check_only:
        INDEX.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
