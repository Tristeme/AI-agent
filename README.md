# AI Workflow Assistant

A production-style AI assistant that integrates LLM reasoning, web search, and retrieval-augmented generation (RAG) for document-based question answering.

---

## Features

- Conversational AI agent (LangChain + OpenAI)
- Web search tool integration (SerpAPI)
- PDF question answering using RAG (FAISS)
- Tool-based orchestration (Agent selects tools automatically)
- Persistent vector store (FAISS index saved locally)
- SQLite chat logging (traceability)
- Logging for tool usage and debugging
- FastAPI backend for API access
- Docker containerisation for deployment

---

## Architecture

```

User
↓
FastAPI / Gradio UI
↓
LangChain Agent
↓
Tools
├── Google Search
└── PDF QA (RAG)
↓
LLM (OpenAI)
↓
Response

```

---

## Tech Stack

- Python 3.11
- LangChain
- OpenAI API
- FAISS (vector database)
- FastAPI
- Gradio
- SQLite
- Docker
- SerpAPI

---

## Project Structure

```

ai-agent-rag/
├── api.py
├── main.py
├── Dockerfile
├── requirements.txt
├── services/
│   ├── llm.py
│   ├── search_tool.py
│   ├── pdf_rag.py
│   ├── db.py
│   └── logger.py
├── storage/
├── logs/

````

---

##  Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
````

### 2. Configure environment variables

Create a `.env` file:

```
OPENAI_API_KEY=your_key
SERPAPI_API_KEY=your_key
```

---

##  Run locally

### Start API

```bash
uvicorn api:app --reload
```

### API Docs

Open in browser:

```
http://127.0.0.1:8000/docs
```

---

##  API Endpoints

### Health Check

```
GET /health
```

---

### Chat

```
POST /chat
```

Request example:

```json
{
  "message": "What tools do you have?"
}
```

---

### Upload PDF

```
POST /upload-pdf
```

---

##  Run with Docker

```bash
docker build -t ai-workflow-assistant .
docker run -p 8000:8000 --env-file .env ai-workflow-assistant
```

---

## 🧠 Key Design Decisions

### 1. Retrieval-Augmented Generation (RAG)

* Grounds responses in uploaded documents
* Reduces hallucination
* Uses FAISS for efficient similarity search

---

### 2. Tool-based Agent

* Dynamically selects tools:

  * Web search for real-time queries
  * PDF QA for document-based queries
* Enables flexible workflow orchestration

---

### 3. Persistence

* FAISS index stored locally
* SQLite used for chat history logging

---

### 4. Observability

* Logging captures:

  * Tool usage
  * Errors
  * System events

---

##  Future Improvements

* Add authentication
* Support multiple PDFs
* Add streaming responses
* Cloud deployment (AWS / GCP)

---

##  Summary

This project demonstrates how to build a production-style AI workflow system by combining LLMs, tool integration, and RAG, with a focus on reliability, traceability, and scalability.
