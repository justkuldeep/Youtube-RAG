import json
from pathlib import Path
from urllib.request import Request, urlopen

# Official lab repository referenced by Google's ADK codelab.
REPO_RAW = "https://raw.githubusercontent.com/cuppibla/adk_tutorial/main"

OUTPUT = Path("data/visual_content.json")

SOURCES = [
    {
        "id": "single_agent_code",
        "type": "code",
        "pattern": "single_agent",
        "title": "Single Agent — official lab source",
        "timestamp": "01:01",
        "start": 61,
        "path": "a_single_agent/day_trip.py",
        "source": "https://github.com/cuppibla/adk_tutorial/blob/main/a_single_agent/day_trip.py",
    },
    {
        "id": "sequential_agent_code",
        "type": "code",
        "pattern": "sequential_agent",
        "title": "Sequential Agent — official lab source",
        "timestamp": "03:05",
        "start": 185,
        "path": "b1_sequential_agent/agents.py",
        "source": "https://github.com/cuppibla/adk_tutorial/blob/main/b1_sequential_agent/agents.py",
    },
    {
        "id": "parallel_agent_code",
        "type": "code",
        "pattern": "parallel_agent",
        "title": "Parallel Agent — official lab source",
        "timestamp": "05:21",
        "start": 321,
        "path": "b2_parallel_agent/agents.py",
        "source": "https://github.com/cuppibla/adk_tutorial/blob/main/b2_parallel_agent/agents.py",
    },
]


def fetch_source(path):
    url = f"{REPO_RAW}/{path}"
    request = Request(
        url,
        headers={"User-Agent": "YouTube-RAG-Project"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    visual_content = []

    for item in SOURCES:
        print(f"Fetching: {item['path']}")

        try:
            code = fetch_source(item["path"])

            visual_content.append({
                "id": item["id"],
                "type": item["type"],
                "pattern": item["pattern"],
                "title": item["title"],
                "timestamp": item["timestamp"],
                "start": item["start"],
                "source": item["source"],
                "content": code
            })

            print(f"  ✓ Loaded {len(code)} characters")

        except Exception as error:
            print(f"  ✗ Failed: {error}")

    with OUTPUT.open("w", encoding="utf-8") as file:
        json.dump(
            visual_content,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\n========================================")
    print("visual_content.json generated!")
    print("========================================")
    print(f"Items: {len(visual_content)}")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()