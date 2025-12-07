import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

vectorsore_path = "vectorstore"
embedding_model = "all-MiniLM-L6-v2"
llm_model = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

class RAG:
    def __init__(self):
        print("Carregando modelo de embeddings...")
        self.embedding_model = SentenceTransformer(embedding_model)

        print("Carregando índice FAISS...")
        self.index = faiss.read_index(f"{vectorsore_path}/index.faiss")

        with open(f"{vectorsore_path}/chunks.pkl", "rb") as f:
            self.chunks = pickle.load(f)

        print("Carregando LLM local...")
        self.llm = pipeline(
            "text-generation",
            model=llm_model,
            device=-1,        
            max_length=1500,
            do_sample=True,
            temperature=0.5
        )

    def retrieve(self, question, k=3):
        question_embedding = self.embedding_model.encode([question]).astype("float32")
        distances, indices = self.index.search(question_embedding, k)
        return [self.chunks[i] for i in indices[0]]

    def generate_answer(self, question):
        contexts = self.retrieve(question)

        context_text = "\n".join(contexts)

        prompt = f"""
Você é um assistente virtual especializado na Universidade do Estado do Amazonas (UEA).
Responda a pergunta usando apenas o contexto fornecido.

Contexto:
{context_text}

Pergunta:
{question}

Resposta:
"""

        response = self.llm(prompt)[0]["generated_text"]

        return response.split("Resposta:")[-1].strip()
