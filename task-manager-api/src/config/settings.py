"""Environment-based configuration. No secrets hardcoded (legacy embedded SECRET_KEY/SMTP)."""
import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(24).hex()
    DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")

    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")

    # Signed-token lifetime (seconds)
    TOKEN_MAX_AGE = int(os.environ.get("TOKEN_MAX_AGE", "3600"))

    # Notifications / SMTP (all from env; disabled by default so no real mail is sent)
    NOTIFICATIONS_ENABLED = os.environ.get("NOTIFICATIONS_ENABLED", "false").lower() == "true"
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")


settings = Settings()
