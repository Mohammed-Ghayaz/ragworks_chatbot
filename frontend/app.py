import streamlit as st
import requests
import json
from streamlit_session_browser_storage import SessionStorage
import os
from typing import List, Dict, Optional

# --- Constants & Configuration ---
BACKEND_URL = "http://localhost:8000"

# Initialize the session storage manager
session_storage = SessionStorage()

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []


# --- Helper Functions for API Calls ---
def get_headers():
    """Returns the authorization headers with the JWT token."""
    token = session_storage.getItem("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# --- Authentication Handlers ---
def handle_login(username, password):
    """Handles the login process and stores the token."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/login",
            data=json.dumps({"username": username, "password": password}),
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            token_data = response.json()
            session_storage.setItem("access_token", token_data["access_token"])
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    except requests.exceptions.ConnectionError:
        st.error("Error: Could not connect to the backend.")

def handle_register(username, email, password):
    """Handles the registration process."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Registration successful! Please log in.")
        else:
            st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
    except requests.exceptions.ConnectionError:
        st.error("Error: Could not connect to the backend.")

def handle_logout():
    """Logs the user out by clearing state and storage."""
    session_storage.deleteItem("access_token")
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.success("You have been logged out.")
    st.rerun()

# --- Conversation Management Functions ---
def fetch_conversations():
    """Fetches all conversations from the backend for the current user."""
    headers = get_headers()
    try:
        response = requests.get(f"{BACKEND_URL}/conversations", headers=headers)
        if response.status_code == 200:
            st.session_state.conversation_history = response.json()
        else:
            st.error(f"Failed to fetch conversations: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Error: Could not connect to the backend to fetch conversations.")

def new_chat_session():
    """Clears the current conversation to start a new one."""
    st.session_state.conversation_id = None
    st.session_state.messages = []
    st.session_state.uploaded_file = None
    st.rerun()

def load_conversation(conv_id, messages):
    st.write("Type of messages:", type(messages))
    st.session_state.conversation_id = conv_id
    if isinstance(messages, str):
        st.session_state.messages = json.loads(messages)
    elif isinstance(messages, list):
        st.session_state.messages = messages
    else:
        st.session_state.messages = []
    st.rerun()


# --- Main App Components ---
def chat_interface():
    """The chatbot UI for interacting with the RAG system."""
    st.header("RAG-Powered Chatbot")

    # Ensure messages is initialized properly
    if "messages" not in st.session_state or not isinstance(st.session_state.messages, list):
        st.session_state.messages = []

    # Display existing messages
    for message in st.session_state.messages:
        if isinstance(message, dict) and "role" in message and "content" in message:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        chat_history_for_api = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages if isinstance(msg, dict)
        ]

        headers = get_headers()
        payload = {
            "query": prompt,
            "chat_history": chat_history_for_api,
            "conversation_id": st.session_state.conversation_id
        }

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                with requests.post(f"{BACKEND_URL}/chat", headers=headers, json=payload, stream=True) as response:
                    if response.status_code != 200:
                        st.error("Error: Could not connect to the chatbot.")
                        return
                    
                    # Extract conversation ID from headers
                    conv_id = response.headers.get("X-Conversation-ID")
                    if conv_id:
                        st.session_state.conversation_id = int(conv_id)

                    # Process incoming stream
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)

                # Append the assistant’s response
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except requests.exceptions.ConnectionError:
                st.error("Error: Could not connect to the backend.")

def upload_file_interface():
    """The file upload UI."""
    st.subheader("Upload a new document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf", key="file_uploader")

    if uploaded_file is not None and not st.session_state.uploaded_file:
        with st.spinner("Processing document..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            headers = get_headers()
            try:
                response = requests.post(f"{BACKEND_URL}/upload", files=files, headers=headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    st.success("Document uploaded and ingested successfully!")
                    st.session_state.uploaded_file = uploaded_file.name
                    # Set the new conversation ID from the backend's response
                    st.session_state.conversation_id = response_data.get("conversation_id")
                    # Clear chat messages and fetch conversations to start new chat with the new document
                    st.session_state.messages = []
                    fetch_conversations()
                else:
                    st.error(f"Failed to upload document: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Error: Could not connect to the backend.")
    elif "uploaded_file" in st.session_state:
        st.info(f"Using previously uploaded file: {st.session_state.uploaded_file}")

def main_app_layout():
    """The main layout for the authenticated user."""
    st.title(f"Welcome, {st.session_state.username}!")
    
    with st.sidebar:
        if st.button("New Chat"):
            new_chat_session()
        st.markdown("---")
        st.subheader("Your Conversations")
        if not st.session_state.conversation_history:
            st.info("Start a new chat to see your history.")
        else:
            for conv in st.session_state.conversation_history:
                try:
                    first_msg = conv['messages'][0]
                    if 'metadata' in first_msg and 'filename' in first_msg['metadata']:
                         display_text = os.path.basename(first_msg['metadata']['filename'])
                    else:
                         display_text = f"Chat {conv['id']}"
                except (KeyError, IndexError, TypeError):
                    display_text = f"Chat {conv['id']}"
                
                if st.button(display_text, key=f"conv_{conv['id']}"):
                    load_conversation(conv['id'], conv['messages'])

    st.button("Logout", on_click=handle_logout, key="logging_out")
    
    upload_file_interface()
    st.markdown("---")
    chat_interface()

def unauthenticated_app_layout():
    """The layout for a user who is not logged in."""
    st.title("Login or Register")
    
    login_tab, register_tab = st.tabs(["Login", "Register"])
    
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login"):
                handle_login(username, password)

    with register_tab:
        with st.form("register_form"):
            username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            if st.form_submit_button("Register"):
                handle_register(username, email, password)

if __name__ == "__main__":
    access_token = session_storage.getItem("access_token")

    if access_token and not st.session_state.get("logged_in", False):
        st.session_state.logged_in = True
        st.session_state.username = "user" 
        st.rerun()
    
    if st.session_state.logged_in and not st.session_state.conversation_history:
        fetch_conversations()
    
    if st.session_state.logged_in:
        main_app_layout()
    else:
        unauthenticated_app_layout()
