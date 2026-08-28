import json
import numpy as np
import chromadb


# ============================================================
# CONFIG
# ============================================================

CHUNKS_FILE = "data/merged_chunks.json"
EMBEDDINGS_FILE = "data/embeddings.npy"

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "youtube_rag_v3"


# ============================================================
# LOAD CHUNKS
# ============================================================

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print(f"Loaded {len(chunks)} unified chunks.")


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

embeddings = np.load(EMBEDDINGS_FILE)

print(f"Loaded {len(embeddings)} embeddings.")
print(f"Embedding shape: {embeddings.shape}")


# ============================================================
# SAFETY CHECK
# ============================================================

if len(chunks) != len(embeddings):
    raise ValueError(
        f"Chunk count ({len(chunks)}) "
        f"does not match embedding count ({len(embeddings)})."
    )


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# Create a NEW collection
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={
        "hnsw:space": "cosine"
    }
)


# ============================================================
# PREPARE DATA
# ============================================================

ids = [
    chunk["chunk_id"]
    for chunk in chunks
]


documents = [
    chunk["content"]
    for chunk in chunks
]


# Chroma metadata must contain primitive values
metadatas = [
    {
        "type": chunk["type"],
        "pattern": chunk["pattern"],
        "title": chunk["title"],
        "timestamp": chunk["timestamp"],
        "start": float(chunk["start"]),
        "end": float(chunk["end"]),
        "source": chunk["source"]
    }
    for chunk in chunks
]


# ============================================================
# STORE
# ============================================================

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)


# ============================================================
# VERIFY
# ============================================================

print("\n" + "=" * 60)
print("CHROMADB STORAGE COMPLETED")
print("=" * 60)

print(f"Collection : {COLLECTION_NAME}")
print(f"Documents  : {collection.count()}")


# ============================================================
# INSPECT DATABASE
# ============================================================

print("\nStored documents:\n")

stored = collection.get(
    include=[
        "documents",
        "metadatas"
    ]
)

for i in range(len(stored["ids"])):

    metadata = stored["metadatas"][i]

    print(
        f"{i + 1}. "
        f"{metadata['type']} | "
        f"{metadata['pattern']} | "
        f"{metadata['timestamp']}"
    )