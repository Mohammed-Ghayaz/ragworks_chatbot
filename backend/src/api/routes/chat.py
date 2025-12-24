from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/chat")
async def chat_with_rag(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.retrieve_text()
    print(data)
    