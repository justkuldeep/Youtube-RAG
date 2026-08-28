import json
import numpy as np
from sentence_transformers import SentenceTransformer


INPUT_FILE = "data/merged_chunks.json"
OUTPUT_FILE = "data/embeddings.npy"

MODEL_NAME = "all-MiniLM-L6-v2"


# --------------------------------------------------
# Load unified chunks
# --------------------------------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as file:
    chunks = json.load(file)

print(f"Loaded {len(chunks)} unified chunks.")


# --------------------------------------------------
# Extract content for embedding
# --------------------------------------------------

texts = [
    chunk["content"]
    for chunk in chunks
]


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

print("\nGenerating embeddings...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    normalize_embeddings=True
)


# --------------------------------------------------
# Save embeddings
# --------------------------------------------------

np.save(
    OUTPUT_FILE,
    embeddings
)


# --------------------------------------------------
# Verify
# --------------------------------------------------

print("\n" + "=" * 50)
print("EMBEDDING GENERATION COMPLETED")
print("=" * 50)

print(f"Chunks              : {len(chunks)}")
print(f"Embedding shape     : {embeddings.shape}")
print(f"Embedding dimension : {embeddings.shape[1]}")
print(f"Saved to            : {OUTPUT_FILE}")