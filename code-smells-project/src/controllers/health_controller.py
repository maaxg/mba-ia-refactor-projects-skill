"""Health + home controllers. Health NEVER exposes secrets/config (unlike the legacy version)."""
from flask import jsonify

from config.settings import settings
from models.db import get_connection

_TABELAS = ("produtos", "usuarios", "pedidos")


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": settings.VERSION,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def health_check():
    conn = get_connection()
    try:
        # Table names are fixed constants (not user input) — safe to interpolate.
        counts = {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in _TABELAS}
    finally:
        conn.close()
    return jsonify({
        "status": "ok",
        "database": "connected",
        "counts": counts,
        "versao": settings.VERSION,
    }), 200
