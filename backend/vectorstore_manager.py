from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_vectorstore(collection_name: str) -> VectorStoreRetriever:
    """
    Returns a retriever for a specific Chroma vector store collection.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    persist_directory = f"./chroma_db"
    
    # This will load the existing collection, not create a new one.
    print(f"Loading existing vector store collection: {collection_name}...")
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_name=collection_name
    )
    
    return vectorstore
