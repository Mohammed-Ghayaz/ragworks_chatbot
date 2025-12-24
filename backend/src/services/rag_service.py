from ..core.llm_client import llm_client
from typing import List
from ..core.config import GEMINI_MODEL
from ..schemas.message import Message
import asyncio
from ..schemas.feedback import Feedback

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
    
def build_retrieval_query(history_summary: str, user_query: str) -> str:
    retrieval_query = f"""
    Conversation context summary:
    {history_summary}

    Current user intent:
    {user_query}

    Retrieve the most relevant document passages.
    """

    return retrieval_query.strip()

async def stream_answer(
    history_summary: str,
    retrieved_chunks: List[dict],
    user_query: str
):
    chunks = [f'[{chunk["payload"]["filename"]}: {chunk["payload"]["chunk_index"]}]\n{chunk["payload"]["text"]}' for chunk in retrieved_chunks]

    prompt = f"""
    Imagine you are a useful assistant, who answers correctly to the user queries.
    You are provided with the conversation summary, retrieved context and user query.
    Make good use of the conversation summary and the retrieved context to answer the user query.
    Make sure you answer only from the retrieved chunks. Answer briefly in 2-3 lines.
    If the retrieved chunks or the conversation provides insufficient context to the user query, just say 'I dont know'.
    Else provide a proper response with citations. Provide the citations in [filename: chunk_index] format.
    If the user message is a greeting or casual conversation (e.g., hi, hello, thanks), you may respond normally without using the retrieved context.

    Conversation Summary:
    {history_summary}

    Retrieved Chunks:
    {"\n\n".join(chunks)}

    User Query:
    {user_query}
    """

    queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    def _blocking_stream():
        try:
            response_stream = llm_client.models.generate_content_stream(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            for chunk in response_stream:
                try:
                    text = chunk.candidates[0].content.parts[0].text
                    if text:
                        loop.call_soon_threadsafe(queue.put_nowait, text)
                except Exception:
                    # Ignore partial / malformed chunks
                    pass
        finally:
            loop.call_soon_threadsafe(queue.put_nowait, None)

    # Run the blocking stream in a background thread
    asyncio.create_task(asyncio.to_thread(_blocking_stream))

    # Async consumer
    while True:
        item = await queue.get()
        if item is None:
            break
        yield item