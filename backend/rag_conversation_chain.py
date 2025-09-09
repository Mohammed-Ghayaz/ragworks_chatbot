from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from vectorstore_manager import get_vectorstore

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_retriever(user_id: int, conversation_id: int):
    collection_name = f"user_{user_id}_docs"
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.as_retriever(search_kwargs={"filter": {"conversation_id": str(conversation_id)}})

def get_rag_chain(user_id: int, conversation_id: int):
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-pro", temperature=0.5, api_key=GOOGLE_API_KEY)
    retriever = get_retriever(user_id, conversation_id)

    history_aware_system_prompt = """
    Imagine you are a very useful assistant. Based on the provided chat history and latest user query, rephrase the query into a standalone question
    which can be used to retrieve relevant documents. Do not answer the user query, just rephrase the user query. If the chat history is empty, return as it is.
    """

    history_aware_prompt = ChatPromptTemplate.from_messages([
        ("system", history_aware_system_prompt),
        MessagesPlaceholder('chat_history'),
        ("user", "{input}")
    ])

    history_aware_chain = create_history_aware_retriever(llm, retriever, history_aware_prompt)

    qa_system_prompt = """
    Imagine you are a QA chatbot, which answers the user query based on the retrieved context and the chat history provided.
    Use the following pieces of retrieved context to generate response.
    If the retrieved context doesn't have the answer to the user query or you don't know the answer, just say you don't know. Don't hallucinate.
    Provide answers for maximum of 3 sentences. Keep the answers concise.

    Context: {context}
    """

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])

    qa_stuff_chain = create_stuff_documents_chain(llm=llm, prompt=qa_prompt)

    conversation_retrieval = create_retrieval_chain(history_aware_chain, qa_stuff_chain)

    return conversation_retrieval
