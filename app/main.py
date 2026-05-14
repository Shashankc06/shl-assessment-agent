from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SHL Assessment Chatbot Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat():
    return {
        "reply": "Chat endpoint working",
        "recommendations": [],
        "end_of_conversation": False
    }