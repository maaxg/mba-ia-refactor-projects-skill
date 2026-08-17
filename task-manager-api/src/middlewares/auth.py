"""Authentication/authorization guards. The legacy app enforced no auth on any endpoint despite
defining User.is_admin(); here EVERY write endpoint (POST/PUT/PATCH/DELETE) requires a valid signed
token. Two guards share one token extractor + verifier so they can't drift:

- require_auth  → any valid token (ordinary content writes: tasks, categories).
- require_admin → valid token AND role == "admin" (account management, privileged reports).
"""
from functools import wraps

from flask import jsonify, request

from services.auth_service import verify_token


def _extract_token():
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):]
    return request.headers.get("X-Auth-Token")


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"error": "Autenticação necessária"}), 401
        if not verify_token(token):
            return jsonify({"error": "Token inválido ou expirado"}), 401
        return fn(*args, **kwargs)

    return wrapper


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
