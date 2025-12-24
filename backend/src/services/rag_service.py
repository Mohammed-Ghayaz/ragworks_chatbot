from ..core.llm_client import llm_client
from typing import List
from ..core.config import GEMINI_MODEL
from ..schemas.message import Message

async def summarize_history(history: List[Message]) -> str:
    try:
        chat_history = ""
        for message in history:
            chat_history += f"{message.role}: {message.content}\n"
        
        summarize_history_prompt = f"""
        Imagine you are a summarization bot, who gets the chat_history which could be a long text or list of long texts.
        Your task is to get the chat_history and summarize it in less than 5 lines, capturing the most important part of the chat.

        Chat History:
        {chat_history}
        """
        response = await llm_client.models.generate_content_async(
            model = GEMINI_MODEL,
            content = summarize_history_prompt
        )

        return response.text

    except Exception as e:
        raise RuntimeError("History summarization failed") from e