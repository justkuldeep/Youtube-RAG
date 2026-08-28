# 🎥 YouTube RAG

A Retrieval-Augmented Generation (RAG) system that allows users to ask questions about the content of a YouTube video.

The project takes a YouTube video, extracts its audio, converts the audio into a transcript, creates semantic chunks and embeddings, stores them in a vector database, and retrieves relevant context to answer user questions.

> 🚧 **Project Status:** Work in Progress
> The current version implements the basic YouTube → Transcript → Embedding → Retrieval → Answer pipeline. Retrieval quality and grounding are being actively improved.

---

## 🧠 What is this project?

YouTube RAG combines:

**YouTube Video → Audio → Transcript → Chunks → Embeddings → Vector Database → Retrieval → LLM Answer**

Instead of asking an LLM to answer a question from its general knowledge, the system retrieves relevant information from the selected video's transcript and uses that information to generate an answer.

This helps the system answer questions specifically about the video.

---

## ✨ Current Features

* 📺 YouTube video ingestion
* 🎵 Audio extraction using `yt-dlp`
* 📝 Audio transcription
* ✂️ Transcript chunking
* 🧮 Text embeddings
* 🗄️ Vector storage using ChromaDB
* 🔎 Semantic similarity search
* 🤖 RAG-based question answering
* 💬 Interactive terminal-based Q&A

---

## 🏗️ Architecture

```text
                 ┌─────────────────┐
                 │   YouTube URL   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     yt-dlp      │
                 │ Audio Extraction│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Audio File     │
                 │   (.mp3)        │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Transcription │
                 │     Whisper     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    Transcript   │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Chunking    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Embeddings    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │    ChromaDB      │
                 │  Vector Storage  │
                 └────────┬────────┘
                          │
                    User Question
                          │
                          ▼
                 ┌─────────────────┐
                 │    Retriever    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │  Relevant Video │
                 │     Context     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │       LLM       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │      Answer     │
                 └─────────────────┘
```

---

## 📁 Project Structure

```text
Youtube-Rag/
│
├── data/
│   ├── chroma_db/          # Generated vector database
│   ├── audio.mp3           # Downloaded audio
│   ├── chunks.json         # Transcript chunks
│   ├── embeddings.npy      # Generated embeddings
│   └── transcript.txt      # Generated transcript
│
├── chunk_transcript.py     # Splits transcript into chunks
├── generate_audio.py       # Downloads/extracts YouTube audio
├── generate_embeddings.py  # Creates embeddings
├── generate_transcript.py  # Converts audio to text
├── retrieve.py             # Retrieves relevant chunks
├── store_embeddings.py     # Stores embeddings in ChromaDB
├── rag.py                  # Main RAG question-answering pipeline
│
├── .env                    # API keys (not committed)
├── .gitignore
└── README.md
```

---

## 🔄 Pipeline

### 1. YouTube → Audio

`generate_audio.py` uses `yt-dlp` to download the audio from the provided YouTube video.

```text
YouTube URL
     ↓
yt-dlp
     ↓
audio.mp3
```

### 2. Audio → Transcript

The extracted audio is converted into text using a speech-to-text model.

```text
audio.mp3
    ↓
Whisper
    ↓
transcript.txt
```

### 3. Transcript → Chunks

The transcript is divided into smaller sections so that relevant information can be retrieved efficiently.

```text
Transcript
    ↓
Chunking
    ↓
chunks.json
```

### 4. Chunks → Embeddings

Each chunk is converted into a vector representation.

```text
Text Chunk
    ↓
Embedding Model
    ↓
Vector
```

### 5. Vector Storage

The generated embeddings are stored in ChromaDB.

```text
Chunks + Embeddings
        ↓
    ChromaDB
```

### 6. Question → Retrieval

When a user asks a question, the question is converted into an embedding and compared with the stored vectors.

```text
User Question
      ↓
Question Embedding
      ↓
Similarity Search
      ↓
Relevant Chunks
```

### 7. Retrieval → Answer

The retrieved context is provided to the LLM to generate an answer grounded in the video transcript.

```text
Question + Retrieved Context
             ↓
            LLM
             ↓
           Answer
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Youtube-Rag.git
cd Youtube-Rag
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
```

Never commit `.env` to GitHub.

The `.env` file is already excluded through `.gitignore`.

---

## ▶️ Running the Pipeline

The project can be executed as a sequential pipeline.

### Step 1 — Download audio

```bash
python generate_audio.py
```

### Step 2 — Generate transcript

```bash
python generate_transcript.py
```

### Step 3 — Create chunks

```bash
python chunk_transcript.py
```

### Step 4 — Generate embeddings

```bash
python generate_embeddings.py
```

### Step 5 — Store embeddings

```bash
python store_embeddings.py
```

### Step 6 — Ask questions

```bash
python rag.py
```

---

## 💬 Example

```text
Ask something (or type 'exit'): What is an AI agent?

Answer:
...
```

The goal is for the answer to be based only on information available in the selected YouTube video.

---

## 🚧 Current Limitations

The current implementation is an early version of the RAG pipeline.

Some areas still need improvement:

* Retrieval can return irrelevant chunks.
* Similarity thresholds need better tuning.
* Answers can sometimes fail to find information that exists in the transcript.
* Transcript chunks currently have limited metadata.
* Timestamp-aware retrieval is not fully implemented.
* Video title and metadata are not yet integrated into the answer generation.
* The system does not yet robustly distinguish between information present and absent in the video.
* Long videos may require better hierarchical retrieval.
* Citation/source tracking is still limited.

These limitations are part of the ongoing development of the project.

---

## 🚀 Future Improvements

The long-term goal is to build a **full-fledged YouTube Video RAG system** capable of answering questions about everything discussed in a video while maintaining strong grounding.

Planned improvements include:

### 🔎 Better Retrieval

* Hybrid search
* Semantic + keyword retrieval
* Reranking
* Better similarity thresholds
* Query expansion
* Metadata filtering

### ⏱️ Timestamp-Aware RAG

Store timestamps with every transcript segment.

```text
[12:34 - 13:02]
The speaker explains how an AI agent works...
```

The system should be able to answer:

> "Where does the video explain AI agents?"

with a timestamp such as:

```text
Around 12:34
```

### 🧠 Better Grounding

The RAG should:

* Answer only from retrieved video context.
* Clearly state when information is not present.
* Avoid filling missing information using the LLM's general knowledge.
* Provide supporting transcript sections.
* Reduce hallucinations.

### 📚 Rich Video Knowledge

The system should eventually understand:

* Video title
* Description
* Transcript
* Chapters
* Timestamps
* Speakers
* Topics
* Technical concepts
* Code discussed in the video
* Examples
* Definitions
* Comparisons
* Questions and answers

---

## 🎯 Project Goal

The final goal is to build a system where a user can provide **any suitable YouTube video** and ask questions such as:

```text
What is the main topic of this video?

Explain the AI agent architecture discussed in the video.

What tools are used by the agent?

Where does the speaker explain RAG?

What code is discussed?

What are the limitations mentioned?

Give me all the concepts related to AI agents discussed in this video.

At what timestamp is this concept explained?
```

The system should respond using information grounded in the video rather than hallucinating information from outside knowledge.

---

## 🛠️ Tech Stack

* **Python**
* **yt-dlp**
* **Whisper**
* **Embeddings**
* **ChromaDB**
* **LLM / Generative AI**
* **RAG**

---

## 📌 Project Status

**Active Development**

Current focus:

> Improving retrieval quality, grounding, metadata, timestamps and hallucination resistance.

---

## 👨‍💻 Author

**Kuldeep Soni**

B.Tech — Artificial Intelligence & Machine Learning

GitHub: [justkuldeep](https://github.com/justkuldeep)

LinkedIn: [justkuldeep](https://www.linkedin.com/in/justkuldeep)
