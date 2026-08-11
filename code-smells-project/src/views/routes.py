"""Routing layer (Views) — maps URL + method → controller function. No logic, no DB.

Preserves the exact HTTP contract of the legacy app. The only changes:
  - POST /admin/query was removed (arbitrary SQL execution).
  - POST /admin/reset-db is now guarded by require_admin.
"""
from controllers import (
    admin_controller,
    health_controller,
    pedido_controller,
    produto_controller,
    relatorio_controller,
    usuario_controller,
)
from middlewares.auth import require_admin


def register_routes(app):
    # Home & health
    app.add_url_rule("/", "index", health_controller.index, methods=["GET"])
    app.add_url_rule("/health", "health_check", health_controller.health_check, methods=["GET"])

    # Produtos
    app.add_url_rule("/produtos", "listar_produtos", produto_controller.listar, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", produto_controller.buscar_query, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", produto_controller.buscar, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", produto_controller.criar, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", produto_controller.atualizar, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", produto_controller.deletar, methods=["DELETE"])

    # Usuarios
    app.add_url_rule("/usuarios", "listar_usuarios", usuario_controller.listar, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", usuario_controller.buscar, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", usuario_controller.criar, methods=["POST"])
    app.add_url_rule("/login", "login", usuario_controller.login, methods=["POST"])

    # Pedidos
    app.add_url_rule("/pedidos", "criar_pedido", pedido_controller.criar, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", pedido_controller.listar_todos, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", pedido_controller.listar_por_usuario, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", pedido_controller.atualizar_status, methods=["PUT"])

    # Relatórios
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", relatorio_controller.relatorio_vendas, methods=["GET"])

    # Admin (guarded)
    app.add_url_rule("/admin/reset-db", "reset_db", require_admin(admin_controller.reset_db), methods=["POST"])
