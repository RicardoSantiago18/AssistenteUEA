import os
import fitz  
import numpy as np
import pickle
import faiss
from sentence_transformers import SentenceTransformer

pdf_path = "data/pdfs"
vectorstore_path = "vectorstore"
embeddind_model = "all-MiniLM-L6-v2"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap

    return chunks

def main():
    print("Iniciando ingestão dos PDFs...")

    all_chunks = []

    for file_name in os.listdir(pdf_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(pdf_path, file_name)
            print(f"📄 Lendo: {file_name}")

            text = extract_text_from_pdf(file_path)
            chunks = chunk_text(text)

            print(f"✅ {len(chunks)} chunks gerados.")
            all_chunks.extend(chunks)

    print("Gerando embeddings...")
    model = SentenceTransformer(embeddind_model)
    embeddings = model.encode(all_chunks)

    embeddings = np.array(embeddings).astype("float32")

    print("Criando índice FAISS...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(vectorstore_path, exist_ok=True)

    faiss.write_index(index, os.path.join(vectorstore_path, "index.faiss"))

    with open(os.path.join(vectorstore_path, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)

    print("Ingestão finalizada com sucesso!")
    print("Vetores salvos em /vectorstore")

if __name__ == "__main__":
    main()
