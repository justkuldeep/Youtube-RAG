import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIG
# ============================================================

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "youtube_rag_v3"

TOP_K = 5


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Connected to {COLLECTION_NAME}"
)
print(
    f"Documents: {collection.count()}"
)


# ============================================================
# DETECT QUESTION TYPE
# ============================================================

def detect_query_type(question):

    question_lower = question.lower()

    code_keywords = [
        "code",
        "implementation",
        "syntax",
        "program",
        "script",
        "write the code",
        "show me the code",
        "give me the code",
        "example code"
    ]

    for keyword in code_keywords:

        if keyword in question_lower:
            return "code"

    return "general"


# ============================================================
# RETRIEVE
# ============================================================

def retrieve(question):

    query_type = detect_query_type(question)

    print(
        f"\nQuery type: {query_type}"
    )

    # --------------------------------------------------------
    # Convert question to embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        question,
        normalize_embeddings=True
    ).tolist()


    # --------------------------------------------------------
    # General retrieval
    # --------------------------------------------------------

    if query_type == "general":

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )


    # --------------------------------------------------------
    # Code retrieval
    # --------------------------------------------------------

    else:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,
            where={
                "type": "code"
            },
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )


    # --------------------------------------------------------
    # Format results
    # --------------------------------------------------------

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved.append({

            "content": document,

            "type": metadata["type"],

            "pattern": metadata["pattern"],

            "title": metadata["title"],

            "timestamp": metadata["timestamp"],

            "start": metadata["start"],

            "end": metadata["end"],

            "source": metadata["source"],

            "distance": distance

        })

    return retrieved


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(results):

    print("\n" + "=" * 70)
    print("RETRIEVED RESULTS")
    print("=" * 70)

    for index, result in enumerate(results):

        print(
            f"\nResult {index + 1}"
        )

        print("-" * 70)

        print(
            f"Type      : {result['type']}"
        )

        print(
            f"Pattern   : {result['pattern']}"
        )

        print(
            f"Timestamp : {result['timestamp']}"
        )

        print(
            f"Distance  : {result['distance']:.4f}"
        )

        print(
            f"\n{result['content']}"
        )


# ============================================================
# TEST LOOP
# ============================================================

while True:

    question = input(
        "\nAsk something (or type 'exit'): "
    )

    if question.lower() == "exit":

        break

    results = retrieve(question)

    display_results(results)