import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS  # Updated import
from langchain_community.embeddings import OpenAIEmbeddings  # Updated import
from langchain_community.document_loaders import PyPDFLoader  # Updated import
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
import gradio as gr
import tempfile

# Load your API keys from .env
load_dotenv()

# === Step 1: Initialize LLM ===
llm = ChatOpenAI(temperature=0, model_name="gpt-4")

# === Step 2: External Tool - Google Search ===
from serpapi import GoogleSearch


def serpapi_search(query: str) -> str:
    params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERPAPI_API_KEY"),
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if "organic_results" in results and len(results["organic_results"]) > 0:
        return results["organic_results"][0].get("snippet", "No snippet found.")
    return "No relevant results found."


search_tool = Tool(
    name="Google Search",
    func=serpapi_search,
    description="Useful for answering questions about current events."
)

# === Step 3: Add Memory ===
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# === Step 4: Create Agent ===
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=True
)


# === Step 5: Define PDF QA Workflow ===
def process_pdf_and_ask(pdf_file, question):
    # Fix for handling Gradio file upload
    if pdf_file is None:
        return "Please upload a PDF file first."

    # Get the file path directly from Gradio file component
    temp_path = pdf_file.name

    # Load and process the PDF
    try:
        loader = PyPDFLoader(temp_path)
        pages = loader.load()

        # Split the document into chunks
        splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(pages)

        # Create vector database
        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.from_documents(docs, embeddings)

        # Create QA chain
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectordb.as_retriever())

        # Run the query
        return qa_chain.run(question)
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


# === Step 6: Gradio Interface ===
def agent_respond(message, history):
    try:
        result = agent.invoke({"input": message})
        return result.get("output", result)
    except Exception as e:
        return f"Error: {e}"


with gr.Blocks() as iface:
    gr.Markdown("# AI Agent with Web Search + PDF QA")

    with gr.Tab("Chat Agent"):
        chat = gr.ChatInterface(fn=agent_respond)

    with gr.Tab("PDF QA"):
        with gr.Row():
            file_input = gr.File(label="Upload PDF")

        with gr.Row():
            question_input = gr.Textbox(label="Ask a question about the PDF", placeholder="What does this PDF discuss?")

        with gr.Row():
            submit_btn = gr.Button("Ask")

        with gr.Row():
            answer_output = gr.Textbox(label="Answer")

        submit_btn.click(fn=process_pdf_and_ask, inputs=[file_input, question_input], outputs=answer_output)

if __name__ == "__main__":
    iface.launch()