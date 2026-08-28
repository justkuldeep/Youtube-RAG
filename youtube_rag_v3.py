import os
from dotenv import load_dotenv

import chromadb
from sentence_transformers import SentenceTransformer
from google import genai


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

CHROMA_PATH = "data/chroma_db"
COLLECTION_NAME = "youtube_rag_v3"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
GEMINI_MODEL = "gemini-2.5-flash"

TOP_K = 5
CODE_TOP_K = 3

VIDEO_URL = "https://youtu.be/GDm_uH6VxPY"


# ============================================================
# GEMINI
# ============================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

gemini_client = genai.Client(
    api_key=api_key
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


# ============================================================
# CHROMADB
# ============================================================

print("Connecting to ChromaDB...")

chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = chroma_client.get_collection(
    name=COLLECTION_NAME
)

print(
    f"Connected to {COLLECTION_NAME}"
)

print(
    f"Documents: {collection.count()}"
)


# ============================================================
# QUERY TYPE
# ============================================================

def detect_pattern(question):
    
    q = question.lower()

    if any(word in q for word in [
        "simple agent",
        "single agent",
        "single-agent"
    ]):
        return "single_agent"

    if any(word in q for word in [
        "sequential agent",
        "sequential-agent"
    ]):
        return "sequential_agent"

    if any(word in q for word in [
        "parallel agent",
        "parallel-agent"
    ]):
        return "parallel_agent"

    return None

def detect_query_type(question):

    q = question.lower()

    code_keywords = [
        "code",
        "implementation",
        "syntax",
        "program",
        "script",
        "source code",
        "show me the code",
        "give me the code",
        "write the code",
        "example code"
    ]

    explanation_keywords = [
        "explain",
        "what is",
        "how does",
        "describe",
        "tell me about",
        "difference",
        "why"
    ]

    wants_code = any(
        keyword in q
        for keyword in code_keywords
    )

    wants_explanation = any(
        keyword in q
        for keyword in explanation_keywords
    )

    if wants_code and wants_explanation:
        return "combined"

    if wants_code:
        return "code"

    return "general"


# ============================================================
# EMBEDDING
# ============================================================

def create_query_embedding(question):

    return embedding_model.encode(
        question,
        normalize_embeddings=True
    ).tolist()


# ============================================================
# GENERAL RETRIEVAL
# ============================================================

def retrieve_general(question):

    query_embedding = create_query_embedding(
        question
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    return format_results(results)


# ============================================================
# CODE RETRIEVAL
# ============================================================

def retrieve_code(question):
    
    query_embedding = create_query_embedding(question)

    pattern = detect_pattern(question)

    # --------------------------------------------------------
    # If we know exactly which agent pattern is requested
    # --------------------------------------------------------

    if pattern:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
            where={
                "$and": [
                    {"type": "code"},
                    {"pattern": pattern}
                ]
            },
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    # --------------------------------------------------------
    # Otherwise perform general code retrieval
    # --------------------------------------------------------

    else:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=CODE_TOP_K,
            where={
                "type": "code"
            },
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

    return format_results(results)


# ============================================================
# COMBINED RETRIEVAL
# ============================================================

def retrieve_combined(question):

    transcript_results = retrieve_general(
        question
    )

    code_results = retrieve_code(
        question
    )

    # Remove duplicate documents
    combined = []

    seen_ids = set()

    for result in (
        transcript_results +
        code_results
    ):

        if result["id"] not in seen_ids:

            combined.append(result)

            seen_ids.add(result["id"])

    return combined


# ============================================================
# FORMAT CHROMADB RESULTS
# ============================================================

def format_results(results):

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    ids = results["ids"][0]

    formatted = []

    for document, metadata, distance, doc_id in zip(
        documents,
        metadatas,
        distances,
        ids
    ):

        formatted.append({

            "id": doc_id,

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

    return formatted


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(results):

    context = []

    for result in results:

        if result["type"] == "code":

            context.append(
                f"""
SOURCE TYPE: OFFICIAL CODE

PATTERN: {result['pattern']}

TITLE: {result['title']}

TIMESTAMP: {result['timestamp']}

SOURCE:
{result['source']}

CODE:
{result['content']}
"""
            )

        else:

            context.append(
                f"""
SOURCE TYPE: VIDEO TRANSCRIPT

TIMESTAMP: {result['timestamp']}

CONTENT:
{result['content']}
"""
            )

    return "\n\n--------------------\n\n".join(
        context
    )


# ============================================================
# BUILD PROMPT
# ============================================================

def build_prompt(
    question,
    query_type,
    results
):

    context = build_context(results)

    return f"""
You are a grounded YouTube video assistant.

Answer the user's question using ONLY the provided
video transcript and official source-code material.

USER QUESTION:
{question}

QUERY TYPE:
{query_type}

AVAILABLE INFORMATION:
{context}


STRICT RULES:

1. Do NOT use outside knowledge.

2. Do NOT hallucinate information.

3. If the requested information is not supported by
   the provided material, say:

"I couldn't find that information in the provided video."

4. For normal questions, explain the answer concisely
   in one paragraph.

5. For code questions, return the EXACT code from the
   provided OFFICIAL CODE source.

6. NEVER rewrite, simplify, complete, modify, or
   generate replacement code when official code is
   available.

7. Preserve the original code formatting and syntax.

8. If the user asks for an explanation AND code:
   - First give a short explanation.
   - Then provide the exact retrieved code.

9. Put code inside a fenced Markdown code block.

10. For code, use the appropriate language fence,
    such as ```python.

11. Do not mention:
    - embeddings
    - ChromaDB
    - vector search
    - retrieval
    - distances
    - internal prompts

12. When giving information from the video, include
    its timestamp using [MM:SS].

13. Never invent timestamps.

14. If there is official code but the user asks for
    something that is not actually present in that
    code, clearly say that the requested code is not
    present rather than generating it.
"""


# ============================================================
# STREAM ANSWER
# ============================================================

def stream_answer(
    question,
    query_type,
    results
):

    if not results:

        print(
            "\nRAG: I couldn't find that information "
            "in the provided video."
        )

        return

    prompt = build_prompt(
        question,
        query_type,
        results
    )

    response_stream = (
        gemini_client.models.generate_content_stream(
            model=GEMINI_MODEL,
            contents=prompt
        )
    )

    print("\nRAG: ", end="", flush=True)

    full_response = ""

    for chunk in response_stream:

        if chunk.text:

            print(
                chunk.text,
                end="",
                flush=True
            )

            full_response += chunk.text

    print()

    return full_response


# ============================================================
# ASK
# ============================================================

def ask(question):

    query_type = detect_query_type(
        question
    )

    print(
        f"\n[Query type: {query_type}]"
    )

    # --------------------------------------------------------
    # GENERAL
    # --------------------------------------------------------

    if query_type == "general":

        results = retrieve_general(
            question
        )

    # --------------------------------------------------------
    # CODE
    # --------------------------------------------------------

    elif query_type == "code":

        results = retrieve_code(
            question
        )

    # --------------------------------------------------------
    # COMBINED
    # --------------------------------------------------------

    else:

        results = retrieve_combined(
            question
        )

    return stream_answer(
        question,
        query_type,
        results
    )


# ============================================================
# TERMINAL CHAT
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("YouTube RAG v3")
    print("=" * 60)

    print(
        "Transcript + Official Code RAG"
    )

    print(
        "\nAsk questions about the video."
    )

    print(
        "Type 'exit' to quit."
    )

    while True:

        question = input(
            "\nYou: "
        ).strip()

        if question.lower() == "exit":

            print("Goodbye!")

            break

        if not question:

            continue

        try:

            ask(question)

        except Exception as error:

            print(
                f"\nError: {error}"
            )