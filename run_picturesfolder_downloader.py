import json
import os
from pathlib import Path

import yt_dlp


BASE_DIR = Path(__file__).resolve().parent
SAVE_FOLDER = Path(os.getenv("SAVE_FOLDER", BASE_DIR / "picturesfolder_downloads"))
URLS_FILE = Path(os.getenv("URLS_FILE", BASE_DIR / "urls.txt"))
SEEN_FILE = Path(os.getenv("SEEN_FILE", BASE_DIR / "seen_tweets.json"))


def load_seen_ids() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    with SEEN_FILE.open("r", encoding="utf-8") as handle:
        return set(json.load(handle))


def save_seen_ids(seen_ids: set[str]) -> None:
    with SEEN_FILE.open("w", encoding="utf-8") as handle:
        json.dump(sorted(seen_ids), handle, indent=2)


def load_urls() -> list[str]:
    if not URLS_FILE.exists():
        raise FileNotFoundError(f"URL list not found: {URLS_FILE}")

    urls: list[str] = []
    with URLS_FILE.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def extract_post_id(post_url: str) -> str:
    return post_url.rstrip("/").split("/")[-1]


def download_video(post_url: str) -> bool:
    ydl_opts = {
        "outtmpl": str(SAVE_FOLDER / "%(upload_date)s_%(id)s_%(title).50s.%(ext)s"),
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(post_url, download=True)
            print(f"Downloaded: {info.get('title', 'Video')}")
        return True
    except Exception as exc:
        print(f"Failed: {post_url} -> {exc}")
        return False


def main() -> int:
    SAVE_FOLDER.mkdir(parents=True, exist_ok=True)
    seen_ids = load_seen_ids()
    urls = load_urls()

    print(f"Loaded {len(urls)} URL(s) from {URLS_FILE}")

    downloaded = 0
    skipped = 0

    for post_url in urls:
        post_id = extract_post_id(post_url)
        if post_id in seen_ids:
            print(f"Skipping already seen post: {post_id}")
            skipped += 1
            continue

        if download_video(post_url):
            seen_ids.add(post_id)
            downloaded += 1

    save_seen_ids(seen_ids)
    print(f"Finished. Downloaded={downloaded}, Skipped={skipped}, Seen={len(seen_ids)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
