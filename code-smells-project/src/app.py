"""Composition root / entry point.

Wires config → DB init → routes → error handlers into a Flask app. This is the ONLY place
that assembles the application. No business logic lives here.

Run from the project directory:  python src/app.py
"""
import logging
import os
import sys

# Make the src/ package importable when launched as `python src/app.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask  # noqa: E402
from flask_cors import CORS  # noqa: E402

from config.settings import settings  # noqa: E402
from middlewares.error_handler import register_error_handlers  # noqa: E402
from models.db import init_db  # noqa: E402
from views.routes import register_routes  # noqa: E402


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app, origins=settings.CORS_ORIGINS)

    init_db()
    register_routes(app)
    register_error_handlers(app)
    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    logging.getLogger(__name__).info(
        "Servidor iniciado em http://%s:%s", settings.HOST, settings.PORT
    )
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
