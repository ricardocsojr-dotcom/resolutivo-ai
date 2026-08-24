# Imagem base oficial leve do Python
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    HOST=0.0.0.0

WORKDIR /app

# Instala dependências de compilação essenciais e limpa cache do apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências do Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia código da aplicação e módulos de skills
COPY . .

# Cria usuário não-root para execução segura
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expõe porta do serviço HTTP
EXPOSE 8000

# Health check nativo do Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização do servidor MCP Streamable HTTP
CMD ["python", "-m", "src.server", "--host", "0.0.0.0", "--port", "8000", "--transport", "streamable-http"]
