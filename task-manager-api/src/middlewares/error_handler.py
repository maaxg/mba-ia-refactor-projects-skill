"""Centralized error handling — replaces the legacy bare `except:` blocks that swallowed errors.
Rolls back the session and returns a safe message; full detail is logged server-side.
"""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from database import db

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http(e):
        return jsonify({"error": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        db.session.rollback()
        logger.exception("Erro não tratado")
        return jsonify({"error": "Erro interno"}), 500
