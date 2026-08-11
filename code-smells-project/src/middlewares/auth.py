"""Authorization guard for admin/destructive endpoints.

Replaces the legacy "no auth at all" on /admin/* routes. Expects an X-Admin-Token header
matching settings.ADMIN_TOKEN (sourced from the environment).
"""
from functools import wraps

from flask import request

from config.exceptions import UnauthorizedError
from config.settings import settings


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Admin-Token")
        if not token or token != settings.ADMIN_TOKEN:
            raise UnauthorizedError("Acesso administrativo negado")
        return fn(*args, **kwargs)

    return wrapper
