import os
import fitz  # PyMuPDF
import numpy as np
import pickle
import faiss
import re
from sentence_transformers import SentenceTransformer

pdf_path = "data/pdfs"
vectorstore_path = "vectorstore"
embedding_model = "all-MiniLM-L6-v2"

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_pages = []
    for page in doc:
        text_pages.append(page.get_text())
    return "\n".join(text_pages)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            last_space = text.rfind(' ', start, end)
            if last_space != -1:
                end = last_space
        
        chunk = text[start:end].strip()
        
        if len(chunk) > 20: 
            chunks.append(chunk)

        start = end - overlap

        if start >= end:
            start = end

    return chunks

def main():
    if not os.path.exists(pdf_path):
        print(f"ERRO: Diretório '{pdf_path}' não encontrado.")
        return

    print("Iniciando ingestão dos PDFs...")
    all_chunks = []

    files = [f for f in os.listdir(pdf_path) if f.lower().endswith(".pdf")]
    if not files:
        print("Nenhum arquivo PDF encontrado.")
        return

    for file_name in files:
        file_path = os.path.join(pdf_path, file_name)
        print(f"Processando: {file_name}")

        raw_text = extract_text_from_pdf(file_path)
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text)

        print(f" -> {len(chunks)} chunks gerados.")
        all_chunks.extend(chunks)

    if not all_chunks:
        print("Nenhum texto extraído. Verifique os PDFs.")
        return

    print(f"Total de chunks a processar: {len(all_chunks)}")
    print("Gerando embeddings (isso pode demorar um pouco)...")
    
    model = SentenceTransformer(embedding_model)
    embeddings = model.encode(all_chunks, show_progress_bar=True)

    embeddings = np.array(embeddings).astype("float32")

    print("Criando índice FAISS...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    os.makedirs(vectorstore_path, exist_ok=True)
    faiss.write_index(index, os.path.join(vectorstore_path, "index.faiss"))

    with open(os.path.join(vectorstore_path, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)

    print("Ingestão finalizada com sucesso!")
    print(f"Arquivos salvos em '{vectorstore_path}/'")

if __name__ == "__main__":
    main()