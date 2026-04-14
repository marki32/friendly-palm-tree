import os
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parent
SAVE_FOLDER = Path(os.getenv("SAVE_FOLDER", BASE_DIR / "picturesfolder_downloads"))
DROPBOX_ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN", "")
DROPBOX_FOLDER = os.getenv("DROPBOX_FOLDER", "/")


def iter_video_files() -> list[Path]:
    if not SAVE_FOLDER.exists():
        return []
    return sorted(path for path in SAVE_FOLDER.iterdir() if path.suffix.lower() == ".mp4")


def upload_file(video_path: Path) -> None:
    if not DROPBOX_ACCESS_TOKEN:
        raise RuntimeError("DROPBOX_ACCESS_TOKEN is not set")

    dest_path = f"{DROPBOX_FOLDER.rstrip('/')}/{video_path.name}"
    headers = {
        "Authorization": f"Bearer {DROPBOX_ACCESS_TOKEN}",
        "Dropbox-API-Arg": f'{{"path": "{dest_path}", "mode": "add", "autorename": true}}',
        "Content-Type": "application/octet-stream",
    }
    with video_path.open("rb") as handle:
        response = requests.post(
            "https://content.dropboxapi.com/2/files/upload",
            headers=headers,
            data=handle,
            timeout=120,
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Dropbox upload failed: {response.text}")

    print(f"Uploaded to Dropbox: {dest_path}")


def main() -> int:
    video_files = iter_video_files()
    if not video_files:
        print("No video files found to upload.")
        return 0

    for video_path in video_files:
        upload_file(video_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
