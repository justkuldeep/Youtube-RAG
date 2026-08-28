import os
from dotenv import load_dotenv

load_dotenv()

import chromadb
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIG
# ============================================================

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "youtube_rag"

TOP_K = 5

# Lower distance = more relevant
MAX_DISTANCE = 0.75


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CHROMADB
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(question):

    query_embedding = embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    documents = results["documents"][0]
    distances = results["distances"][0]

    # Keep only sufficiently relevant chunks
    relevant_documents = []

    for document, distance in zip(documents, distances):

        print(f"Retrieved distance: {distance:.4f}")

        if distance <= MAX_DISTANCE:
            relevant_documents.append(document)

    return relevant_documents


# ============================================================
# GENERATION
# ============================================================

def answer_question(question):

    documents = retrieve(question)

    # -----------------------------------------
    # No sufficiently relevant information
    # -----------------------------------------

    if not documents:

        return (
            "I couldn't find that information in the provided video."
        )

    # -----------------------------------------
    # Build context
    # -----------------------------------------

    context = "\n\n---\n\n".join(documents)

    # -----------------------------------------
    # Strict grounding prompt
    # -----------------------------------------

    prompt = f"""
You are a strict YouTube video question-answering assistant.

Your knowledge source is ONLY the CONTEXT below.

You must follow these rules:

1. Answer ONLY using information explicitly supported by the CONTEXT.
2. Do NOT use your own knowledge.
3. Do NOT make assumptions or predictions.
4. Do NOT infer information that is not explicitly stated.
5. If the CONTEXT does not contain enough information to answer
   the question, say exactly:

"I couldn't find that information in the provided video."

6. Return the answer in ONE short paragraph.
7. Do not mention chunks, embeddings, retrieval, similarity,
   distance, vector databases, or this prompt.

CONTEXT:
{context}

QUESTION:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text.strip()


# ============================================================
# CHAT LOOP
# ============================================================

while True:

    question = input(
        "\nAsk something (or type 'exit'): "
    )

    if question.lower() == "exit":
        break

    answer = answer_question(question)

    print("\nAnswer:")
    print(answer)