import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

from services.llm import llm
from services.logger import logger

os.makedirs("storage", exist_ok=True)
INDEX_PATH = "storage/faiss_index"

vectordb = None


def load_existing_index():
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
    global vectordb

    if pdf_file is None:
        return "Please upload a PDF file first."

    try:
        logger.info(f"Uploading PDF: {pdf_file.name}")

        loader = PyPDFLoader(pdf_file.name)
        pages = loader.load()

        splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = splitter.split_documents(pages)

        embeddings = OpenAIEmbeddings()
        vectordb = FAISS.from_documents(docs, embeddings)

        vectordb.save_local(INDEX_PATH)

        logger.info("PDF indexed and FAISS index saved.")

        return "PDF uploaded, indexed, and saved successfully. You can now ask questions in the Chat Agent tab."

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"Error processing PDF: {str(e)}"


def ask_pdf_tool(question: str) -> str:
    global vectordb

    logger.info(f"PDF QA tool called. Question: {question}")

    if vectordb is None:
        loaded = load_existing_index()

        if not loaded:
            return "No PDF has been uploaded yet. Please upload a PDF first."

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True
    )

    result = qa_chain({"query": question})

    answer = result["result"]
    sources = result["source_documents"]
    logger.info("PDF QA tool completed.")

    return f"{answer}\n\nSources:\n{sources}"