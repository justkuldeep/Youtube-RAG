import json


# ============================================================
# FILES
# ============================================================

TRANSCRIPT_FILE = "data/chunks.json"
VISUAL_FILE = "data/visual_content.json"

OUTPUT_FILE = "data/merged_chunks.json"


# ============================================================
# LOAD TRANSCRIPT CHUNKS
# ============================================================

with open(
    TRANSCRIPT_FILE,
    "r",
    encoding="utf-8"
) as file:

    transcript_chunks = json.load(file)


print(
    f"Transcript chunks loaded: "
    f"{len(transcript_chunks)}"
)


# ============================================================
# LOAD VISUAL / CODE CONTENT
# ============================================================

with open(
    VISUAL_FILE,
    "r",
    encoding="utf-8"
) as file:

    visual_content = json.load(file)


print(
    f"Visual/code chunks loaded: "
    f"{len(visual_content)}"
)


# ============================================================
# NORMALIZE TRANSCRIPT CHUNKS
# ============================================================

merged_chunks = []

for chunk in transcript_chunks:

    merged_chunks.append({

        "chunk_id": f"transcript_{chunk['chunk_id']}",

        "type": "transcript",

        "title": "Video Transcript",

        "pattern": "general",

        "timestamp": chunk["timestamp"],

        "start": float(chunk["start"]),

        "end": float(chunk["end"]),

        "content": chunk["text"],

        "source": "youtube_transcript"

    })


# ============================================================
# ADD OFFICIAL CODE CHUNKS
# ============================================================

for item in visual_content:

    merged_chunks.append({

        "chunk_id": item["id"],

        "type": item["type"],

        "title": item["title"],

        "pattern": item["pattern"],

        "timestamp": item["timestamp"],

        "start": float(item["start"]),

        # Code is a whole source file, so end is not important.
        "end": float(item["start"]),

        "content": item["content"],

        "source": item["source"]

    })


# ============================================================
# SAVE
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        merged_chunks,
        file,
        indent=2,
        ensure_ascii=False
    )


# ============================================================
# SUMMARY
# ============================================================

transcript_count = sum(
    1
    for chunk in merged_chunks
    if chunk["type"] == "transcript"
)

code_count = sum(
    1
    for chunk in merged_chunks
    if chunk["type"] == "code"
)


print("\n" + "=" * 60)
print("MERGE COMPLETED")
print("=" * 60)

print(
    f"Transcript chunks : {transcript_count}"
)

print(
    f"Code chunks       : {code_count}"
)

print(
    f"Total chunks      : {len(merged_chunks)}"
)

print(
    f"Saved to          : {OUTPUT_FILE}"
)