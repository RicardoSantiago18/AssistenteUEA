# Assistente Virtual UEA - Desafio LLM/RAG

Este projeto consiste em um sistema de **RAG (Retrieval-Augmented Generation)** desenvolvido para o processo seletivo do Projeto ADA. O objetivo é responder perguntas sobre documentos institucionais da Universidade do Estado do Amazonas  utilizando um modelo de linguagem (LLM) rodando localmente.

## 🏗️ Arquitetura Geral

O sistema é composto por três módulos principais:

1.  **Pipeline de Ingestão (`src/ingest.py`)**:
    * Lê os PDFs armazenados na pasta `data/pdfs/`.
    * Extrai o texto utilizando a biblioteca **PyMuPDF (fitz)**.
    * Divide o texto em *chunks* de 500 caracteres (com sobreposição de 50 caracteres).
    * Gera embeddings utilizando o modelo **SentenceTransformer** (`all-MiniLM-L6-v2`).
    * Indexa e armazena os vetores utilizando o **FAISS** (CPU) para recuperação eficiente.

2.  **Pipeline RAG (`src/rag.py`)**:
    * Carrega o índice FAISS e os chunks processados.
    * Utiliza o modelo de linguagem **TinyLlama-1.1B-Chat-v1.0** (quantizado/otimizado para execução local via Hugging Face Transformers).
    * Ao receber uma pergunta, converte-a em embedding, recupera os 3 trechos mais relevantes e constrói um prompt enriquecido com esse contexto.
    * Gera a resposta final baseada estritamente no contexto recuperado.

3.  **API HTTP (`api/main.py`)**:
    * Desenvolvida com **FastAPI**.
    * Expõe o endpoint `/ask` para interação com o usuário.

---

## 🚀 Como Rodar o Projeto

### Opção 1: Via Docker (Recomendado)

O projeto está totalmente "dockerizado" para facilitar a execução. O comando de execução do container já realiza a ingestão dos documentos e sobe a API.

1.  **Construir a imagem:**
    ```bash
    docker build -t assistente-uea .
    ```

2.  **Rodar o container:**
    ```bash
    docker run -p 8000:8000 assistente-uea
    ```
    *Aguarde alguns instantes enquanto o script realiza a ingestão dos PDFs e carrega o modelo LLM na memória.*

### Opção 2: Execução Local

Caso prefira rodar fora do Docker, siga os passos:

1.  **Instalar dependências:**
    Recomenda-se usar um ambiente virtual (venv).
    ```bash
    pip install -r requirements.txt
    ```

2.  **Gerar o Índice (Ingestão):**
    Execute o script para processar os PDFs e criar o banco vetorial.
    ```bash
    python src/ingest.py
    ```

3.  **Iniciar a API:**
    ```bash
    uvicorn api.main:app --host 0.0.0.0 --port 8000
    ```

---

## 📡 Como Chamar a API

A API estará disponível em `http://localhost:8000`.
Acesse: `http://localhost:8000/docs`

### Endpoint: `POST /ask`

Recebe uma pergunta e retorna a resposta gerada pelo LLM.

* **Exemplo de Requisição (cURL):**
    ```bash
    curl -X POST "http://localhost:8000/ask" \
         -H "Content-Type: application/json" \
         -d '{"question": "Quais são os requisitos para a Casa do Estudante?"}'
    ```

* **Corpo da Requisição (JSON):**
    ```json
    {
      "question": "Quais são os requisitos para a Casa do Estudante?"
    }
    ```

* **Exemplo de Resposta:**
    ```json
    {
      "answer": "Para concorrer a uma vaga, o aluno deve estar regularmente matriculado..."
    }
    ```

### Endpoint: `GET /health`

Verifica se a API está online.

---

## ✅ Funcionalidades Implementadas

Conforme os requisitos do desafio, as seguintes funcionalidades foram implementadas:

* [x] **Pipeline de Ingestão de Documentos**: Script automatizado para leitura de PDFs, chunking e indexação vetorial.
* [x] **Execução de Modelo LLM Local**: Uso do `TinyLlama-1.1B` rodando em CPU via biblioteca `transformers`.
* [x] **Pipeline de RAG**: Integração entre busca vetorial (FAISS) e geração de texto para respostas contextualizadas.
* [x] **API HTTP (FastAPI)**: Endpoint funcional para consulta.
* [x] **Docker**: `Dockerfile` otimizado configurado para instalar dependências e executar a aplicação.

---

## Observações e Limitações

Este projeto utiliza o modelo **TinyLlama-1.1B**, que é um *Small Language Model* (SLM) otimizado para rodar em ambientes com recursos limitados (como CPUs comuns). Embora eficiente para o propósito deste desafio, ele possui limitações inerentes:

1.  **Alucinações (Hallucinations)**: Devido ao seu tamanho reduzido de parâmetros (1.1B), o modelo pode ocasionalmente gerar respostas que não estão totalmente alinhadas com o contexto fornecido ou inventar informações quando a resposta não é encontrada nos documentos.
2.  **Seguimento de Instruções**: A capacidade de seguir instruções complexas no prompt é inferior a modelos maiores (como Llama-3-8B ou GPT-4). Em alguns casos, ele pode ser verboso ou repetir partes do texto.
3.  **Desempenho em CPU**: Embora leve, a inferência em CPU é naturalmente mais lenta do que em GPU. O tempo de resposta pode variar dependendo do hardware onde o Docker está sendo executado.
4.  **Janela de Contexto**: O modelo possui uma janela de contexto limitada. Se os trechos recuperados pelo RAG forem muito longos, informações do início do prompt podem ser "esquecidas" ou truncadas.
