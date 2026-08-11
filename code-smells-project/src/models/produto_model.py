"""Produto data access — parameterized SQL only."""
from models.db import get_connection


def _to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def listar_todos():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM produtos").fetchall()
        return [_to_dict(r) for r in rows]
    finally:
        conn.close()


def buscar_por_id(produto_id):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return _to_dict(row) if row else None
    finally:
        conn.close()


def criar(nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def atualizar(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
            "categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def deletar(produto_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def buscar(termo=None, categoria=None, preco_min=None, preco_max=None):
    """Dynamic search with fully parameterized filters (no string interpolation)."""
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = f"%{termo}%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [_to_dict(r) for r in rows]
    finally:
        conn.close()
