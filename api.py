from dotenv import load_dotenv
load_dotenv()

import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

from services.llm import llm
from services.search_tool import search_tool
from services.pdf_rag import upload_pdf, ask_pdf_tool, load_existing_index
from services.db import init_db, save_chat_log
from services.logger import logger


app = FastAPI(title="AI Workflow Assistant API")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


init_db()
load_existing_index()
logger.info("FastAPI application started.")


memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


pdf_tool = Tool(
    name="PDF QA",
    func=ask_pdf_tool,
    description="Use this tool when the user asks questions about the uploaded PDF document."
)


agent = initialize_agent(
    tools=[search_tool, pdf_tool],
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=True
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = agent.invoke({"input": request.message})
        response = result.get("output", result)

        save_chat_log(request.message, response)

        return ChatResponse(response=response)

    except Exception as e:
        error_message = f"Error: {e}"
        logger.error(error_message)
        save_chat_log(request.message, error_message)

        return ChatResponse(response=error_message)


@app.post("/upload-pdf")
def upload_pdf_api(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        class TempFile:
            name = tmp_path

        result = upload_pdf(TempFile())

        return {"message": result}

    except Exception as e:
        logger.error(f"Upload PDF API error: {e}")
        return {"message": f"Error: {e}"}