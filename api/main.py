from fastapi import FastAPI
from pydantic import BaseModel
from src.rag import RAG

app = FastAPI(title="Assistente Virtual UEA")

rag = RAG()

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    answer = rag.generate_answer(request.question)
    return {"answer": answer}

@app.get("/health")
def health_check():
    return {"status": "ok"}
