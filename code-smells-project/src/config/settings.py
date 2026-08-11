"""Application configuration — all values sourced from environment variables.

No secrets are hardcoded here. Sensible non-secret defaults are provided for local
development; production must supply SECRET_KEY / ADMIN_TOKEN via the environment.
"""
import os


class Settings:
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24).hex()
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token-change-me")

    # Runtime
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))

    # Database
    DB_PATH = os.environ.get("DB_PATH", "loja.db")

    # CORS — comma-separated allowlist (no blanket wildcard by default)
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

    # App metadata
    VERSION = "1.0.0"


settings = Settings()
