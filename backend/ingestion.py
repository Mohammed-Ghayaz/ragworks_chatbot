import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def ingest_data(file_path: str, user_id: int, conversation_id: int, filename: str):
    print(f"Ingesting data from {file_path} for user {user_id}...")
    
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # Add metadata for conversation ID and filename to each document
    for doc in documents:
        doc.metadata['conversation_id'] = str(conversation_id)
        doc.metadata['filename'] = filename

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Use a single collection name for the user
    collection_name = f"user_{user_id}_docs"
    persist_directory = f"./chroma_db"

    # Create the vector store. This will add to an existing collection or create a new one.
    vectorstore = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=persist_directory,
        collection_name=collection_name
    )

    print("Data ingestion complete.")
    return {"message": "Data ingested successfully"}
