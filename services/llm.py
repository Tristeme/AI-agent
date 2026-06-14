from langchain_openai import ChatOpenAI

# Shared LLM instance used by the agent and PDF QA workflow
llm = ChatOpenAI(
    temperature=0,
    model_name="gpt-4"
)