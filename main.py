# Load environment variables from .env before importing services
from dotenv import load_dotenv
load_dotenv()

import gradio as gr

# LangChain components for agent and conversation memory
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

# Project services
from services.llm import llm
from services.search_tool import search_tool
from services.pdf_rag import upload_pdf, ask_pdf_tool, load_existing_index
from services.logger import logger

from services.db import init_db, save_chat_log
init_db()

load_existing_index()
logger.info("Application started.")

pdf_tool = Tool(
    name="PDF QA",
    func=ask_pdf_tool,
    description="Useful for answering questions about an uploaded PDF document."
)

# Create conversation memory for the chat agent
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# Create a conversational agent with Google Search tool
agent = initialize_agent(
    tools=[search_tool, pdf_tool],
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=True
)

# Handle messages from the Chat Agent tab
def agent_respond(message, history):
    try:
        result = agent.invoke({"input": message})
        response = result.get("output", result)

        save_chat_log(message, response)

        return response

    except Exception as e:
        error_message = f"Error: {e}"
        save_chat_log(message, error_message)
        return error_message

# Build Gradio user interface
with gr.Blocks() as iface:
    gr.Markdown("# AI Agent with Web Search + PDF QA")

    # Tab 1: general AI chat agent with web search
    with gr.Tab("Chat Agent"):
        gr.ChatInterface(fn=agent_respond)

    # Tab 2: upload a PDF and ask questions about its content
    with gr.Tab("PDF Upload"):
        file_input = gr.File(label="Upload PDF")
        upload_btn = gr.Button("Upload and Index PDF")
        upload_output = gr.Textbox(label="Status")

        upload_btn.click(
            fn=upload_pdf,
            inputs=file_input,
            outputs=upload_output
        )


if __name__ == "__main__":
    iface.launch()