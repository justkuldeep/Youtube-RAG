from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from youtube_rag_v3 import (
    retrieve_general,
    retrieve_code,
    retrieve_combined,
    detect_query_type,
    build_prompt,
    gemini_client,
    GEMINI_MODEL
)


app = FastAPI(title="YouTube RAG API")


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request model
# --------------------------------------------------

class QuestionRequest(BaseModel):
    question: str


# --------------------------------------------------
# Streaming RAG
# --------------------------------------------------

def stream_answer(question: str):
    
    query_type = detect_query_type(question)

    # -----------------------------------------
    # Retrieve according to question type
    # -----------------------------------------

    if query_type == "general":

        results = retrieve_general(question)

    elif query_type == "code":

        results = retrieve_code(question)

    else:

        results = retrieve_combined(question)


    # -----------------------------------------
    # No evidence
    # -----------------------------------------

    if not results:

        yield "I couldn't find that information in the provided video."
        return


    # -----------------------------------------
    # Build grounded prompt
    # -----------------------------------------

    prompt = build_prompt(
        question,
        query_type,
        results
    )


    # -----------------------------------------
    # Gemini streaming
    # -----------------------------------------

    response_stream = gemini_client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=prompt
    )


    # -----------------------------------------
    # Stream to browser
    # -----------------------------------------

    for chunk in response_stream:

        if chunk.text:

            yield chunk.text


# --------------------------------------------------
# API endpoint
# --------------------------------------------------

@app.post("/ask")
def ask_question(request: QuestionRequest):

    return StreamingResponse(
        stream_answer(request.question),
        media_type="text/plain"
    )


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "YouTube RAG v2"
    }