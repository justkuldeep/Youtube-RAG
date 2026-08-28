import yt_dlp

url = "https://youtu.be/GDm_uH6VxPY?si=PlvATg_ECcDGx4We"

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "data/audio.%(ext)s",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])

print("Audio downloaded!")