import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import whisper
import json


AUDIO_FILE = "data/audio.mp3"
OUTPUT_FILE = "data/transcript.json"


print("Loading Whisper...")

model = whisper.load_model("base")

print("Transcribing...")

result = model.transcribe(
    AUDIO_FILE,
    fp16=False,
    word_timestamps=True
)

segments = []

for segment in result["segments"]:

    segments.append({
        "start": segment["start"],
        "end": segment["end"],
        "text": segment["text"].strip(),
        "words": segment.get("words", [])
    })


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        segments,
        file,
        indent=2,
        ensure_ascii=False
    )


print("Timestamped transcript saved!")