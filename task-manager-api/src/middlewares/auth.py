"""Authorization guards. The legacy app enforced no auth on any endpoint despite defining
User.is_admin(); here admin/destructive routes require a valid signed token with the admin role.
"""
from functools import wraps

from flask import jsonify, request

from services.auth_service import verify_token


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):]
    return request.headers.get("X-Auth-Token")


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Autenticação necessária"}), 401
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Token inválido ou expirado"}), 401
        if payload.get("role") != "admin":
            return jsonify({"error": "Acesso restrito a administradores"}), 403
        return fn(*args, **kwargs)

    return wrapper
