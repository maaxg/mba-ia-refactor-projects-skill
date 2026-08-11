"""Usuario data access — parameterized SQL, hashed passwords, no secret leakage."""
from werkzeug.security import generate_password_hash, check_password_hash

from models.db import get_connection


def _to_dict(row):
    """Public serialization — NEVER exposes the password hash."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def listar_todos():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()
        return [_to_dict(r) for r in rows]
    finally:
        conn.close()


def buscar_por_id(usuario_id):
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        return _to_dict(row) if row else None
    finally:
        conn.close()


def criar(nome, email, senha, tipo="cliente"):
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def autenticar(email, senha):
    """Verify credentials against the stored hash. Returns the safe user dict or None."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        if row and check_password_hash(row["senha"], senha):
            return _to_dict(row)
        return None
    finally:
        conn.close()
