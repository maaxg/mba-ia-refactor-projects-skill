"""Produto controller — orchestrates request → model → response. No SQL, no routing here."""
from flask import jsonify, request

from config.exceptions import NotFoundError
from controllers.validators import parse_optional_float, validate_produto
from models import produto_model


def listar():
    return jsonify({"dados": produto_model.listar_todos(), "sucesso": True}), 200


def buscar(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar():
    dados = validate_produto(request.get_json(silent=True))
    novo_id = produto_model.criar(**dados)
    return jsonify({"dados": {"id": novo_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(id):
    if not produto_model.buscar_por_id(id):
        raise NotFoundError("Produto não encontrado")
    dados = validate_produto(request.get_json(silent=True))
    produto_model.atualizar(id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(id):
    if not produto_model.buscar_por_id(id):
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_query():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria", None)
    preco_min = parse_optional_float(request.args.get("preco_min"), "preco_min")
    preco_max = parse_optional_float(request.args.get("preco_max"), "preco_max")
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
