from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.services.chat_service import generate_reply

app = FastAPI()


# Message schema
class Message(BaseModel):
    role: str
    content: str


# Request schema
class ChatRequest(BaseModel):
    messages: List[Message]


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    messages = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in request.messages
    ]

    response = generate_reply(messages)

    return response