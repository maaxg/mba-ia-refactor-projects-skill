"""Category controller — CRUD with aggregate task counts and orphan-safe delete."""
from flask import jsonify, request
from sqlalchemy import func

from config.constants import DEFAULT_COLOR
from database import db
from models.category import Category
from models.task import Task


def list_categories():
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )
    categories = Category.query.all()
    result = [{**c.to_dict(), "task_count": counts.get(c.id, 0)} for c in categories]
    return jsonify(result), 200


def create_category():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400
    name = data.get("name")
    if not name:
        return jsonify({"error": "Nome é obrigatório"}), 400

    category = Category()
    category.name = name
    category.description = data.get("description", "")
    category.color = data.get("color", DEFAULT_COLOR)

    db.session.add(category)
    db.session.commit()
    return jsonify(category.to_dict()), 201


def update_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]
    if "color" in data:
        category.color = data["color"]

    db.session.commit()
    return jsonify(category.to_dict()), 200


def delete_category(cat_id):
    category = db.session.get(Category, cat_id)
    if not category:
        return jsonify({"error": "Categoria não encontrada"}), 404
    # Avoid orphaned FKs: detach tasks from the category before deleting it.
    Task.query.filter_by(category_id=cat_id).update({"category_id": None})
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Categoria deletada"}), 200
