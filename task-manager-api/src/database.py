"""Shared SQLAlchemy instance, initialized by the app factory (no import-time create_all)."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
