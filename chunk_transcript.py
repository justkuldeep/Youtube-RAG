import json


INPUT_FILE = "data/transcript.json"
OUTPUT_FILE = "data/chunks.json"

# Target chunk size
MAX_CHARS = 1200

# Small overlap between chunks
OVERLAP_SEGMENTS = 1


def format_timestamp(seconds):
    """Convert seconds into HH:MM:SS or MM:SS."""

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    return f"{minutes:02d}:{secs:02d}"


# --------------------------------------------------
# Load timestamped transcript
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    transcript = json.load(file)


print(f"Loaded {len(transcript)} transcript segments.")


# --------------------------------------------------
# Create timestamp-aware chunks
# --------------------------------------------------

chunks = []

current_segments = []
current_length = 0

chunk_id = 0


for segment in transcript:

    text = segment["text"].strip()

    if not text:
        continue

    segment_length = len(text)

    # If adding this segment would make the chunk
    # too large, save the current chunk first.
    if current_segments and current_length + segment_length > MAX_CHARS:

        start_time = current_segments[0]["start"]
        end_time = current_segments[-1]["end"]

        chunk_text = " ".join(
            s["text"].strip()
            for s in current_segments
        )

        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text,
            "start": start_time,
            "end": end_time,
            "timestamp": format_timestamp(start_time),
            "type": "transcript"
        })

        chunk_id += 1

        # Keep the last segment as overlap
        current_segments = current_segments[
            -OVERLAP_SEGMENTS:
        ]

        current_length = sum(
            len(s["text"])
            for s in current_segments
        )

    # Add current segment
    current_segments.append(segment)
    current_length += segment_length


# --------------------------------------------------
# Add final chunk
# --------------------------------------------------

if current_segments:

    start_time = current_segments[0]["start"]
    end_time = current_segments[-1]["end"]

    chunk_text = " ".join(
        s["text"].strip()
        for s in current_segments
    )

    chunks.append({
        "chunk_id": chunk_id,
        "text": chunk_text,
        "start": start_time,
        "end": end_time,
        "timestamp": format_timestamp(start_time),
        "type": "transcript"
    })


# --------------------------------------------------
# Save chunks
# --------------------------------------------------

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        chunks,
        file,
        indent=2,
        ensure_ascii=False
    )


# --------------------------------------------------
# Statistics
# --------------------------------------------------

print("\nChunking completed!")
print(f"Total chunks: {len(chunks)}")
print(f"Saved to: {OUTPUT_FILE}")

print("\nFirst chunk:")
print(json.dumps(
    chunks[0],
    indent=2,
    ensure_ascii=False
))