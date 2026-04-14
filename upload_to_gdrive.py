import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BASE_DIR = Path(__file__).resolve().parent
SAVE_FOLDER = Path(os.getenv("SAVE_FOLDER", BASE_DIR / "picturesfolder_downloads"))
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID", "1Tr81azh0890emP6i2pF7l55nGuDjUgDR")
# Can be a path to a file or the JSON string itself
GDRIVE_CREDENTIALS = os.getenv("GDRIVE_CREDENTIALS_JSON", str(BASE_DIR / "camera-f5682-0157c9a591c2.json"))

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def get_gdrive_service():
    if Path(GDRIVE_CREDENTIALS).exists():
        creds = service_account.Credentials.from_service_account_file(
            GDRIVE_CREDENTIALS, scopes=SCOPES
        )
    else:
        # Assume it's a JSON string
        info = json.loads(GDRIVE_CREDENTIALS)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=SCOPES
        )
    return build("drive", "v3", credentials=creds)


def iter_video_files() -> list[Path]:
    if not SAVE_FOLDER.exists():
        return []
    return sorted(path for path in SAVE_FOLDER.iterdir() if path.suffix.lower() == ".mp4")


def upload_file(service, video_path: Path) -> None:
    print(f"Uploading {video_path.name} to Google Drive...")
    
    file_metadata = {
        "name": video_path.name,
        "parents": [GDRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True
    )
    
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    print(f"Successfully uploaded! File ID: {file.get('id')}")


def main() -> int:
    try:
        video_files = iter_video_files()
        if not video_files:
            print("No video files found to upload.")
            return 0

        service = get_gdrive_service()
        for video_path in video_files:
            upload_file(service, video_path)
            
        return 0
    except Exception as e:
        print(f"Error during Google Drive upload: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
