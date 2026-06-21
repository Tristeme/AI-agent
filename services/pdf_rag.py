import os

# FAISS vector store for local similarity search
from langchain_community.vectorstores import FAISS

# OpenAI embeddings convert text chunks into vectors
from langchain_community.embeddings import OpenAIEmbeddings

# PDF loader for extracting text from uploaded PDF files
from langchain_community.document_loaders import PyPDFLoader

# Text splitter divides long documents into smaller chunks for retrieval
from langchain.text_splitter import CharacterTextSplitter

# RetrievalQA combines retrieval + LLM answering
from langchain.chains import RetrievalQA

# Shared LLM instance
from services.llm import llm

# Application logger for observability
from services.logger import logger


# Ensure storage directory exists for local FAISS persistence
os.makedirs("storage", exist_ok=True)

# Local path where the FAISS index is stored
INDEX_PATH = "storage/faiss_index"

# In-memory vector database shared by the PDF upload flow and PDF QA tool
vectordb = None


def load_existing_index():
    """
    Load an existing FAISS index from local storage.

    This allows the system to reuse previously uploaded and indexed documents
    after the application restarts.
    """
    global vectordb

    embeddings = OpenAIEmbeddings()

    if os.path.exists(INDEX_PATH):
        vectordb = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info("Existing FAISS index loaded.")
        return True

    return False


def upload_pdf(pdf_file):
    """
    Process an uploaded PDF and build a persistent FAISS vector index.

    Workflow:
    1. Load PDF pages
    2. Split text into chunks
    3. Generate embeddings
    4. Store chunks in FAISS
    5. Save FAISS index locally
    """
    global vectordb

    if pdf_file is None:
        return "Please upload a PDF file first."

    try:
        logger.info(f"Uploading PDF: {pdf_file.name}")

        # Load PDF content
        loader = PyPDFLoader(pdf_file.name)
        pages = loader.load()

        # Split long PDF text into retrievable chunks
        splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = splitter.split_documents(pages)

        # Create embeddings and build FAISS vector store
        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.from_documents(docs, embeddings)

        # Persist vector index for future reuse
        vectordb.save_local(INDEX_PATH)

        logger.info("PDF indexed and FAISS index saved.")

        return "PDF uploaded, indexed, and saved successfully. You can now ask questions in the Chat Agent tab."

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"Error processing PDF: {str(e)}"


def ask_pdf_tool(question: str) -> str:
    """
    Answer a user question using the uploaded PDF as grounding context.

    If no in-memory vector store exists, the system attempts to load
    the persisted FAISS index from disk.
    """
    global vectordb

    logger.info(f"PDF QA tool called. Question: {question}")

    # Load persisted FAISS index if not already available in memory
    if vectordb is None:
        loaded = load_existing_index()

        if not loaded:
            return "No PDF has been uploaded yet. Please upload a PDF first."

    # Build RetrievalQA chain with source documents enabled
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True
    )

    # Run RAG query
    result = qa_chain({"query": question})

    answer = result["result"]
    sources = result["source_documents"]

    logger.info("PDF QA tool completed.")

    # Return both answer and retrieved sources for traceability
    return f"{answer}\n\nSources:\n{sources}"