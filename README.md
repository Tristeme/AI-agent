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
- Evaluation
- Human-in-the-loop ticket draft generation
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
│   ├── logger.py
│   └── ticket_tool.py
├── storage/
├── logs/
├── evaluation/
├── evaluate.py
├── evaluation.json

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
### Evaluation

This project includes a simple evaluation script to test whether the AI assistant can answer domain-specific questions based on uploaded documents.

## 1. Prepare evaluation questions
In the `evaluation.json` file in the project root:

##  Upload a PDF first

Before running evaluation, upload the PDF in the evaluation_doc:

POST /upload-pdf

The PDF should contain the information needed to answer the evaluation questions.

##  Run evaluation
```bash
python3 evaluate.py
```
##  Example output

Question: What should I do if an inverter has an overheating alarm?

Answer: If an inverter has an overheating alarm, you should first turn off the inverter and disconnect it from the power source. Allow it to cool down for a while. Check for any obstructions or dust in the cooling fan or vents, and clean them if necessary. Ensure the inverter is in a well-ventilated area and not exposed to direct sunlight or other heat sources. If the problem persists, it may be due to a fault in the inverter's cooling system or other internal components, and you should contact a professional or the manufacturer's customer service for further assistance.

Result: PASS

Question: How should I handle a communication failure alarm?

Answer: If you encounter a communication failure alarm, it typically means there's a problem with the connection between the inverter and your monitoring system. Here are some steps you can take: 1. Check the physical connections: Ensure all cables are properly connected and not damaged. 2. Check the network settings: If your inverter communicates over a network (like Wi-Fi or Ethernet), ensure it's properly connected to the network. 3. Restart the inverter: Sometimes, simply restarting the inverter can resolve communication issues. 4. Consult the manual: Your inverter's manual may have specific troubleshooting steps for a communication failure alarm. 5. Contact support: If you're unable to resolve the issue yourself, it may be best to contact the manufacturer's support team for assistance.

Result: PASS

====================
Passed: 2/2
Accuracy: 100.0%


##  Run with Docker

```bash
docker build -t ai-workflow-assistant .
docker run -p 8000:8000 --env-file .env ai-workflow-assistant
```

## Ticket Draft (Human-in-the-loop)

The system includes a ticket drafting capability to support operational workflows without executing real actions.

### How it works

- When a user requests an operational action (e.g. creating a work order),  
  the agent **does not execute the action automatically**.
- Instead, it generates a **draft ticket** for human review.

### Example

User request:

```text
Create a work order for inverter alarm A102
```
System response:

```text
DRAFT TICKET

Issue:
inverter alarm A102

Status:
NOT EXECUTED

Note:
This is only a draft. No work order has been created or submitted.
```
---

## Key Design Decisions

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
