"""Centralized error handling — one place that turns exceptions into safe responses.

Replaces the legacy per-route `except Exception as e: jsonify({"erro": str(e)})` that leaked
internal/DB/SQL text to clients. Full detail is logged server-side; clients get safe messages.
"""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from config.exceptions import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"erro": e.message, "sucesso": False}), e.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"erro": e.description, "sucesso": False}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
