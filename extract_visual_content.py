import os
import json
import cv2
import yt_dlp

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

VIDEO_URL = "https://youtu.be/GDm_uH6VxPY?si=PlvATg_ECcDGx4We"

VIDEO_FILE = "data/video.mp4"
OUTPUT_FILE = "data/visual_content.json"

FRAME_DIR = "data/frames"

# Analyze one frame every N seconds
FRAME_INTERVAL = 5


# ============================================================
# GEMINI
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs("data", exist_ok=True)
os.makedirs(FRAME_DIR, exist_ok=True)


# ============================================================
# DOWNLOAD VIDEO
# ============================================================

def download_video():

    if os.path.exists(VIDEO_FILE):

        print("video.mp4 already exists.")
        return

    print("Downloading YouTube video...")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": VIDEO_FILE,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        ydl.download([VIDEO_URL])

    print("Video downloaded!")


# ============================================================
# FORMAT TIMESTAMP
# ============================================================

def format_timestamp(seconds):

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


# ============================================================
# EXTRACT FRAMES
# ============================================================

def extract_frames():

    print("\nExtracting frames...")

    cap = cv2.VideoCapture(VIDEO_FILE)

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open video.mp4"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = frame_count / fps

    print(f"FPS: {fps:.2f}")
    print(f"Duration: {duration:.2f} seconds")

    frames = []

    current_time = 0

    while current_time < duration:

        cap.set(
            cv2.CAP_PROP_POS_MSEC,
            current_time * 1000
        )

        success, frame = cap.read()

        if not success:
            break

        timestamp = format_timestamp(current_time)

        filename = (
            f"{FRAME_DIR}/"
            f"frame_{int(current_time):06d}.jpg"
        )

        cv2.imwrite(
            filename,
            frame,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                85
            ]
        )

        frames.append({
            "timestamp": timestamp,
            "seconds": current_time,
            "file": filename
        })

        current_time += FRAME_INTERVAL

    cap.release()

    print(
        f"Extracted {len(frames)} frames."
    )

    return frames


# ============================================================
# ANALYZE FRAME WITH GEMINI VISION
# ============================================================

def analyze_frame(frame):

    with open(
        frame["file"],
        "rb"
    ) as image_file:

        image_bytes = image_file.read()

    prompt = """
Analyze this frame from a YouTube video about AI agent design patterns.

We are building a searchable knowledge base.

Determine whether this frame contains useful information that
should be stored for a RAG system.

Pay special attention to:

1. SOURCE CODE
2. CODE SNIPPETS
3. SLIDES
4. DIAGRAMS
5. TABLES
6. IMPORTANT TECHNICAL TEXT
7. AI agent concepts
8. Agent architecture
9. Agent workflows
10. Tool/function definitions

Ignore:
- presenter faces
- decorative graphics
- YouTube controls
- logos
- empty screens
- irrelevant background elements

Return ONLY valid JSON in this exact structure:

{
  "useful": true,
  "type": "code",
  "title": "Short description",
  "content": "Detailed transcription/explanation of all useful visible content"
}

Allowed values for "type":

"code"
"slide"
"diagram"
"text"
"architecture"
"other"

If the frame contains no useful information, return:

{
  "useful": false,
  "type": "other",
  "title": "",
  "content": ""
}

IMPORTANT:
If code is visible, transcribe the code as accurately as possible.
Preserve indentation and syntax as much as possible.
Do not invent missing code.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )
        ]
    )

    text = response.text.strip()

    # Remove markdown JSON fences if Gemini adds them
    if text.startswith("```json"):
        text = text[7:]

    if text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:

        result = json.loads(text)

    except json.JSONDecodeError:

        print(
            f"Could not parse Gemini response "
            f"for {frame['timestamp']}"
        )

        return None

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("VISUAL CONTENT EXTRACTION")
    print("=" * 60)

    # 1. Download video
    download_video()

    # 2. Extract frames
    frames = extract_frames()

    visual_content = []

    # 3. Analyze frames
    for index, frame in enumerate(frames):

        print(
            f"\nAnalyzing frame "
            f"{index + 1}/{len(frames)} "
            f"[{frame['timestamp']}]"
        )

        result = analyze_frame(frame)

        if result is None:
            continue

        # Only store useful frames
        if result.get("useful"):

            item = {
                "timestamp": frame["timestamp"],
                "start": frame["seconds"],
                "type": result.get(
                    "type",
                    "other"
                ),
                "title": result.get(
                    "title",
                    ""
                ),
                "content": result.get(
                    "content",
                    ""
                )
            }

            visual_content.append(item)

            print(
                f"  ✓ Useful: {item['type']}"
            )

        else:

            print("  - Not useful")

    # 4. Save JSON
    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            visual_content,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n" + "=" * 60)
    print("VISUAL EXTRACTION COMPLETED")
    print("=" * 60)

    print(
        f"Useful visual items: "
        f"{len(visual_content)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()