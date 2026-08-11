"""Pedido controller — order flow. Business rules live here; persistence lives in the model."""
from flask import jsonify, request

from config.constants import STATUS_VALIDOS
from config.exceptions import ValidationError
from models import pedido_model
from services import notification_service


def criar():
    dados = request.get_json(silent=True) or {}
    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    resultado = pedido_model.criar(usuario_id, itens)
    notification_service.notificar_pedido_criado(resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_por_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos():
    return jsonify({"dados": pedido_model.listar_todos(), "sucesso": True}), 200


def atualizar_status(pedido_id):
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")
    if novo_status not in STATUS_VALIDOS:
        raise ValidationError("Status inválido")
    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_status_pedido(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
