import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

def get_llm(model: str = "mini"):
    model_name = (
        "claude-haiku-4-5-20251001"
        if model == "mini"
        else "claude-sonnet-4-6"
    )
    return ChatAnthropic(
        model=model_name,
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.3,
    )

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
