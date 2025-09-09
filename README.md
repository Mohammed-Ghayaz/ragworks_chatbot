# RAGworks Chatbot
## Project Overview
This is a full-stack, RAG (Retrieval-Augmented Generation) powered chatbot built as a submission for the RAGworks.ai recruitment process. The application allows users to securely upload PDF documents and engage in conversations with a chatbot that uses the document's content for context.

The project is built with a modern tech stack, demonstrating key skills in backend development, front-end design, and conversational AI engineering.

## Key Features
**User Authentication**: Secure user registration and login using JWT (JSON Web Tokens).

**Persistent Sessions**: User sessions are maintained across browser refreshes using client-side storage.

**Document Ingestion**: Users can upload PDF documents, which are processed and stored in a vector database.

**Conversational AI**: A chatbot interface powered by Google's Gemini-Pro model and LangChain for context-aware responses.

**Data Isolation**: Each user's uploaded documents are stored in a private, dedicated vector database collection to ensure security and privacy.

## Tech Stack
**Backend**: FastAPI (Python) for building a high-performance, asynchronous API.

**Frontend**: Streamlit (Python) for a clean, interactive, and easy-to-deploy user interface.

**RAG Framework**: LangChain for orchestrating the RAG pipeline.

**LLM**: Google's Gemini-Pro for generating intelligent responses.

**Vector Database**: ChromaDB for storing and retrieving document embeddings.

**Database**: SQLite with SQLAlchemy for persistent user data and chat history.

## Setup and Installation
### Prerequisites
Python 3.8+

A valid Google AI API key for Gemini.

### Detailed Setup Process
**Clone the repository and set up a virtual environment.**

Start by cloning the project from your Git repository. Then, create a virtual environment to manage dependencies and activate it.

```
git clone [https://github.com/Mohammed-Ghayaz/ragworks_chatbot.git](https://github.com/Mohammed-Ghayaz/ragworks_chatbot.git)
cd ragworks_chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install the required Python packages.**

You'll need to install all the libraries listed in the requirements.txt file. If this file doesn't exist yet, you can create it by running pip freeze > requirements.txt once all dependencies are installed.

```
pip install -r requirements.txt
```

**Configure your API key.**

Create a file named .env in the root of your project directory and add your Google AI API key. This key is used by the Gemini model.

```
GOOGLE_API_KEY="your_api_key_here"
SECRET_HASH_KEY="your_hash_key"
DATABASE_URL="database_url"
```

This file should be added to your .gitignore to prevent it from being committed to your repository.

**Create tables.**

Before starting the application, run the `database.py` file to create tables

```
python backend/ingest.py
```

**Run the application.**

Open two separate terminal windows. In the first terminal, run the FastAPI backend. In the second, run the Streamlit frontend. This allows both services to run simultaneously.

In the first terminal (for the backend):

```
cd backend
uvicorn main:app --reload
```

In the second terminal (for the frontend):

```
cd frontend
streamlit run app.py
```

The application should now be running in your browser at http://localhost:8501.

## Usage
**Register a New User**: On the main page, navigate to the "Register" tab to create a new account.

**Login**: Use your newly created credentials to log in. Your session will persist even if you refresh the page.

**Upload a Document**: Use the file uploader to add a new PDF. This will create a new, isolated conversation, and the chatbot will be ready to answer questions about the document.

**Start Chatting**: Ask questions related to the content of your uploaded document. The RAG chatbot will provide a streaming, context-aware response.

## Note

When you navigate to the previous chat, it collects all the infomation related to that particular conversation, and you can continue to chat. But, the frontend might not display the previous chat.