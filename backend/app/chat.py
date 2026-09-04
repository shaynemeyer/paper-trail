# app/chat.py
from functools import lru_cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

from app.config import CHAT_MODEL, OLLAMA_BASE_URL


@lru_cache
def get_chat_client() -> ChatOllama:
    return ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_BASE_URL)


async def ask(question: str, context: str) -> str:
    system_prompt = (
        "You are a helpful assistant that answers questions about this document. "
        "Answer only using the context below; say so if the answer isn't in it.\n\n"
        f"{context}"
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
    response = await get_chat_client().ainvoke(messages)
    return response.content
