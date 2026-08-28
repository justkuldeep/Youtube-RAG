import yt_dlp
import json

URL = "https://youtu.be/GDm_uH6VxPY?si=PlvATg_ECcDGx4We"

options = {
    "skip_download": True,
}

with yt_dlp.YoutubeDL(options) as ydl:

    info = ydl.extract_info(URL, download=False)

metadata = {
    "video_id": info.get("id"),
    "title": info.get("title"),
    "description": info.get("description"),
    "channel": info.get("channel"),
    "channel_id": info.get("channel_id"),
    "duration": info.get("duration"),
    "upload_date": info.get("upload_date"),
    "webpage_url": info.get("webpage_url"),
    "chapters": info.get("chapters"),
    "categories": info.get("categories"),
    "tags": info.get("tags"),
}

with open(
    "data/metadata.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        metadata,
        file,
        indent=2,
        ensure_ascii=False
    )

print("Metadata saved!")
print("Title:", metadata["title"])
print("Duration:", metadata["duration"])