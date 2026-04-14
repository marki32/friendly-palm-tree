import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


BASE_DIR = Path(__file__).resolve().parent
SAVE_FOLDER = Path(os.getenv("SAVE_FOLDER", BASE_DIR / "picturesfolder_downloads"))
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")


def iter_video_files() -> list[Path]:
    if not SAVE_FOLDER.exists():
        return []
    return sorted(path for path in SAVE_FOLDER.iterdir() if path.suffix.lower() == ".mp4")


def build_drive_service():
    if not SERVICE_ACCOUNT_JSON.strip():
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is not set")

    info = json.loads(SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/drive.file"],
    )
    return build("drive", "v3", credentials=credentials)


def upload_file(service, video_path: Path) -> None:
    metadata = {
        "name": video_path.name,
        "parents": [DRIVE_FOLDER_ID],
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4", resumable=True)
    created = service.files().create(
        body=metadata,
        media_body=media,
        fields="id,name",
        supportsAllDrives=True,
    ).execute()
    print(f"Uploaded to Google Drive: {created['name']} ({created['id']})")


def main() -> int:
    if not DRIVE_FOLDER_ID:
        raise RuntimeError("GOOGLE_DRIVE_FOLDER_ID is not set")

    video_files = iter_video_files()
    if not video_files:
        print("No video files found to upload.")
        return 0

    service = build_drive_service()
    for video_path in video_files:
        upload_file(service, video_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
