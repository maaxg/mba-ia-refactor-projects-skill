"""Composition root / entry point — app factory that wires config, DB, blueprints and
error handling. No business logic here.

Run from the project directory:  python src/seed.py  then  python src/app.py
"""
import logging
import os
import sys

# Make the src/ package importable when launched as `python src/app.py`.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify  # noqa: E402
from flask_cors import CORS  # noqa: E402

from config.settings import settings  # noqa: E402
from database import db  # noqa: E402
from middlewares.error_handler import register_error_handlers  # noqa: E402
from utils.timeutils import now_utc  # noqa: E402


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = settings.SECRET_KEY

    CORS(app, origins=settings.CORS_ORIGINS)
    db.init_app(app)

    # Import models (register tables) and blueprints inside the factory.
    from models import Category, Task, User  # noqa: F401
    from views.category_routes import category_bp
    from views.report_routes import report_bp
    from views.task_routes import task_bp
    from views.user_routes import user_bp

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(category_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "timestamp": str(now_utc())})

    @app.route("/")
    def index():
        return jsonify({"message": "Task Manager API", "version": "1.0"})

    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
