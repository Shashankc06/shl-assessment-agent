from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


@app.get("/")
def home():
    return {"message": "SHL Assessment Chatbot Running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.messages[-1].content

    return {
        "reply": f"You said: {user_message}",
        "recommendations": [],
        "end_of_conversation": False
    }