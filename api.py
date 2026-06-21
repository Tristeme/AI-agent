from dotenv import load_dotenv
load_dotenv()

import shutil
import tempfile

# FastAPI core components
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

# LangChain components for agent + memory
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

# Internal services (modularised system design)
from services.llm import llm
from services.search_tool import search_tool
from services.pdf_rag import upload_pdf, ask_pdf_tool, load_existing_index
from services.db import init_db, save_chat_log
from services.logger import logger
from services.ticket_tool import ticket_tool


# Create FastAPI app
app = FastAPI(title="AI Workflow Assistant API")


# =========================
# Request / Response models
# =========================

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# =========================
# System initialization
# =========================

# Initialise database (SQLite for traceability)
init_db()

# Load existing FAISS index if available (persistence for RAG)
load_existing_index()

logger.info("FastAPI application started.")


# =========================
# Memory (conversation state)
# =========================

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


# =========================
# Tool definitions
# =========================

# PDF QA tool (RAG-based retrieval)
pdf_tool = Tool(
    name="PDF QA",
    func=ask_pdf_tool,
    description="Use this tool when the user asks questions about the uploaded PDF document."
)

# =========================
# Agent (core orchestration layer)
# =========================

agent = initialize_agent(
    tools=[search_tool, pdf_tool, ticket_tool],  # multi-tool system
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=True  # enables reasoning trace (debugging / observability)
)


# =========================
# API endpoints
# =========================

# Health check (used for monitoring / deployment readiness)
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Chat endpoint (main entry point for AI system)
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Agent decides:
        # - direct LLM response
        # - or call Search / RAG / Ticket tools
        result = agent.invoke({"input": request.message})

        # Extract final answer
        response = result.get("output", result)

        # Save interaction (traceability + audit)
        save_chat_log(request.message, response)

        return ChatResponse(response=response)

    except Exception as e:
        error_message = f"Error: {e}"

        # Log error for debugging
        logger.error(error_message)

        # Persist error as well (observability)
        save_chat_log(request.message, error_message)

        return ChatResponse(response=error_message)


# PDF upload endpoint (builds vector store for RAG)
@app.post("/upload-pdf")
def upload_pdf_api(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Wrap temp file to match existing interface
        class TempFile:
            name = tmp_path

        # Process PDF → chunk → embed → FAISS index
        result = upload_pdf(TempFile())

        return {"message": result}

    except Exception as e:
        logger.error(f"Upload PDF API error: {e}")
        return {"message": f"Error: {e}"}