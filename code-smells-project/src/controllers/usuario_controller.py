"""Usuario controller — user CRUD + login. Delegates auth to the model (hashed)."""
from flask import jsonify, request

from config.exceptions import NotFoundError, UnauthorizedError
from controllers.validators import validate_usuario
from models import usuario_model


def listar():
    return jsonify({"dados": usuario_model.listar_todos(), "sucesso": True}), 200


def buscar(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar():
    dados = validate_usuario(request.get_json(silent=True))
    novo_id = usuario_model.criar(dados["nome"], dados["email"], dados["senha"])
    return jsonify({"dados": {"id": novo_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise UnauthorizedError("Email e senha são obrigatórios")
    usuario = usuario_model.autenticar(email, senha)
    if not usuario:
        raise UnauthorizedError("Email ou senha inválidos")
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
