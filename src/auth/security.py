"""Módulo de segurança, sanitização de logs e configuração do Resolutivo.AI."""

import os
import re
import time
import logging
from typing import Optional, Dict, Any
import jwt

# ─── Configurações de Ambiente ───────────────────────────────────────────────

AUTH_MODE = os.environ.get("AUTH_MODE", "none").lower()  # "none", "bearer", "oauth"
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "gemini-mcp-client")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", "change-me-in-production")
JWT_SECRET = os.environ.get("JWT_SECRET", "resolutivo-ai-jwt-secret-key-change-me")
SERVER_BASE_URL = os.environ.get("SERVER_BASE_URL", "http://localhost:8000")
DATAJUD_APIKEY = os.environ.get(
    "DATAJUD_API_KEY",
    "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
)

# ─── Sanitização de Logs ────────────────────────────────────────────────────

# Padrões sensíveis: Tokens, Chaves, CPFs, CNPJs, Números de processo CNJ
SENSITIVE_PATTERNS = [
    (re.compile(r"Bearer\s+([A-Za-z0-9_\-\.]+)", re.IGNORECASE), "Bearer [REDACTED]"),
    (re.compile(r"APIKey\s+([A-Za-z0-9_\-\.=+]+)", re.IGNORECASE), "APIKey [REDACTED]"),
    (re.compile(r"(\b\d{3}\.\d{3}\.\d{3}\-\d{2}\b)"), "[CPF REDACTED]"),
    (re.compile(r"(\b\d{2}\.\d{3}\.\d{3}/\d{4}\-\d{2}\b)"), "[CNPJ REDACTED]"),
    (re.compile(r"(\b\d{7}\-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\b)"), "[PROC REDACTED]"),
    (re.compile(r'("?(?:password|client_secret|secret|api_key|token)"?\s*[:=]\s*)"[^"]+"', re.IGNORECASE), r'\1"[REDACTED]"'),
]

def sanitize_log_message(msg: str) -> str:
    """Remove dados sensíveis de mensagens de log."""
    if not isinstance(msg, str):
        return str(msg)
    sanitized = msg
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized

class SafeLogFilter(logging.Filter):
    """Filtro de logging para sanitização automática de mensagens e argumentos."""
    def filter(self, record: logging.LogRecord) -> bool:
        if record.msg and isinstance(record.msg, str):
            record.msg = sanitize_log_message(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: sanitize_log_message(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(sanitize_log_message(str(v)) for v in record.args)
        return True

def get_safe_logger(name: str = "resolutivo-ai") -> logging.Logger:
    """Retorna um logger configurado com filtro de segurança."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s"))
        logger.addHandler(handler)
    logger.addFilter(SafeLogFilter())
    logger.setLevel(logging.INFO)
    return logger

logger = get_safe_logger()

# ─── JWT & Token Helpers ────────────────────────────────────────────────────

def create_access_token(client_id: str, scope: str = "mcp:all", expires_in: int = 3600) -> str:
    """Gera um JWT assinado para autenticação OAuth 2.1."""
    now = int(time.time())
    payload = {
        "iss": SERVER_BASE_URL,
        "sub": client_id,
        "aud": "resolutivo-ai-mcp",
        "iat": now,
        "exp": now + expires_in,
        "scope": scope,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica e decodifica um token Bearer ou JWT."""
    # 1. Se for API Key estática direta
    if MCP_API_KEY and token == MCP_API_KEY:
        return {"sub": "api-key-user", "scope": "mcp:all"}

    # 2. Se for JWT OAuth
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="resolutivo-ai-mcp",
            options={"verify_exp": True}
        )
        return payload
    except Exception as e:
        logger.debug(f"Falha na validação do token: {type(e).__name__}")
        return None
