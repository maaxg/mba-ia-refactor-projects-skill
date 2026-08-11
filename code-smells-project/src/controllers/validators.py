"""Shared input validators — one source of truth, reused by create and update flows.

Raises ValidationError (mapped to HTTP 400 by the centralized error handler) instead of
letting bad input reach the DB or blow up as an unhandled 500.
"""
import re

from config.constants import (
    CATEGORIAS_VALIDAS,
    CATEGORIA_PADRAO,
    NOME_MAX_LEN,
    NOME_MIN_LEN,
)
from config.exceptions import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _to_number(value, field, integer=False):
    try:
        return int(value) if integer else float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Campo '{field}' deve ser numérico")


def validate_produto(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"'{campo}' é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    preco = _to_number(dados["preco"], "preco")
    estoque = _to_number(dados["estoque"], "estoque", integer=True)

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if not isinstance(nome, str) or len(nome) < NOME_MIN_LEN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_MAX_LEN:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError(f"Categoria inválida. Válidas: {CATEGORIAS_VALIDAS}")

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validate_usuario(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not _EMAIL_RE.match(email):
        raise ValidationError("Email inválido")
    return {"nome": nome, "email": email, "senha": senha}


def parse_optional_float(value, field):
    if value is None:
        return None
    return _to_number(value, field)
