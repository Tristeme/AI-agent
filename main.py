import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, Tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from serpapi import GoogleSearch
import gradio as gr

# Load your API keys from .env
load_dotenv()

# === Step 1: Initialize LLM ===
llm = ChatOpenAI(temperature=0, model_name="gpt-4")

# === Step 2: Create SerpAPI Tool Manually ===
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

# === Step 3: Add Memory - FIXED ===
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# === Step 4: Create Agent ===
agent = initialize_agent(
    tools=[search_tool],
    llm=llm,
    agent="chat-conversational-react-description",
    memory=memory,
    verbose=True
)

# === Step 5: Gradio Interface ===
def agent_respond(message, history):
    try:
        result = agent.invoke({"input": message})
        return result.get("output", result)
    except Exception as e:
        return f"Error: {e}"

iface = gr.ChatInterface(fn=agent_respond, title="AI Agent with Web Search + Memory")

if __name__ == "__main__":
    iface.launch()