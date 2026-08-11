"""Signed-token auth — replaces the legacy predictable 'fake-jwt-token-<id>'.

Uses itsdangerous (ships with Flask) to sign a token with SECRET_KEY, so tokens are
tamper-evident and expire. No new dependency required.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config.settings import settings

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="auth-token")


def generate_token(user):
    return _serializer.dumps({"user_id": user.id, "role": user.role})


def verify_token(token):
    try:
        return _serializer.loads(token, max_age=settings.TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
