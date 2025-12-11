# Usa uma imagem leve do Python 3.9
FROM python:3.10-slim

# Define variáveis de ambiente para evitar arquivos .pyc e logs em buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho no container
WORKDIR /app

# Instala dependências do sistema necessárias para compilar pacotes (se necessário)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
# O flag --no-cache-dir ajuda a reduzir o tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código do projeto para o container
COPY . .

# Expõe a porta que o FastAPI usará
EXPOSE 8000

# Comando para rodar a ingestão (opcional, mas recomendado garantir que o índice exista) 
# e subir a API. 
# NOTA: Em produção real, a ingestão geralmente é um passo separado, 
# mas para este desafio, garantir que o índice existe ao iniciar facilita a avaliação.
CMD python src/ingest.py && uvicorn api.main:app --host 0.0.0.0 --port 8000