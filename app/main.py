from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SHL Assessment Chatbot Running"}

@app.get("/health")
def health():
    return {"status": "ok"}