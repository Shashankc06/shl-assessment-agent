from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

from app.services.chat_service import generate_reply


app = FastAPI(
    title="Talent Assessment Assistant",
    version="1.0.0",
    swagger_ui_parameters={
        "displayRequestDuration": True
    }
)

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@app.get("/")
def home():
    return {
        "message": "SHL Assessment Chatbot Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    result = generate_reply(
        [msg.dict() for msg in request.messages]
    )

    return result