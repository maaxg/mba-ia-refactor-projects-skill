"""Admin controller — destructive operations, protected by the require_admin guard.

The legacy arbitrary-SQL endpoint (POST /admin/query) was REMOVED: there is no safe place
in an MVC app to execute attacker-supplied SQL. Only the gated reset remains.
"""
from flask import jsonify

from models.db import get_connection

_TABELAS = ("itens_pedido", "pedidos", "produtos", "usuarios")


def reset_db():
    conn = get_connection()
    try:
        for tabela in _TABELAS:
            conn.execute(f"DELETE FROM {tabela}")
        conn.commit()
    finally:
        conn.close()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
