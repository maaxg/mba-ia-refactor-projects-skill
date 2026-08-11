"""Task controller — business flow. No routing here; models handle persistence."""
import logging
from datetime import datetime

from flask import jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from config.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
)
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from services import notification_service
from utils.timeutils import now_utc

logger = logging.getLogger(__name__)


def _serialize(task):
    data = task.to_dict()
    data["overdue"] = task.is_overdue()
    return data


def _validate_title(title):
    if not title:
        return "Título é obrigatório"
    if len(title) < MIN_TITLE_LENGTH:
        return "Título muito curto"
    if len(title) > MAX_TITLE_LENGTH:
        return "Título muito longo"
    return None


def _validate_priority(value):
    try:
        p = int(value)
    except (ValueError, TypeError):
        return None, "Prioridade inválida"
    if not Task.validate_priority(p):
        return None, f"Prioridade deve ser entre {MIN_PRIORITY} e {MAX_PRIORITY}"
    return p, None


def _parse_due_date(value):
    if not value:
        return None, None
    try:
        return datetime.strptime(value, DATE_FORMAT), None
    except (ValueError, TypeError):
        return None, "Formato de data inválido. Use YYYY-MM-DD"


def list_tasks():
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data["overdue"] = t.is_overdue()
        data["user_name"] = t.user.name if t.user else None
        data["category_name"] = t.category.name if t.category else None
        result.append(data)
    return jsonify(result), 200


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    return jsonify(_serialize(task)), 200


def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    title = data.get("title")
    err = _validate_title(title)
    if err:
        return jsonify({"error": err}), 400

    status = data.get("status", DEFAULT_STATUS)
    if not Task.validate_status(status):
        return jsonify({"error": "Status inválido"}), 400

    priority, perr = _validate_priority(data.get("priority", DEFAULT_PRIORITY))
    if perr:
        return jsonify({"error": perr}), 400

    user_id = data.get("user_id")
    if user_id and not db.session.get(User, user_id):
        return jsonify({"error": "Usuário não encontrado"}), 404

    category_id = data.get("category_id")
    if category_id and not db.session.get(Category, category_id):
        return jsonify({"error": "Categoria não encontrada"}), 404

    due_date, derr = _parse_due_date(data.get("due_date"))
    if derr:
        return jsonify({"error": derr}), 400

    task = Task()
    task.title = title
    task.description = data.get("description", "")
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id
    task.due_date = due_date
    tags = data.get("tags")
    if tags:
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info("Task criada: %s - %s", task.id, task.title)

    if task.user_id and task.user:
        notification_service.notify_task_assigned(task.user, task)

    return jsonify(_serialize(task)), 201


def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    if "title" in data:
        err = _validate_title(data["title"])
        if err:
            return jsonify({"error": err}), 400
        task.title = data["title"]

    if "description" in data:
        task.description = data["description"]

    if "status" in data:
        if not Task.validate_status(data["status"]):
            return jsonify({"error": "Status inválido"}), 400
        task.status = data["status"]

    if "priority" in data:
        priority, perr = _validate_priority(data["priority"])
        if perr:
            return jsonify({"error": perr}), 400
        task.priority = priority

    if "user_id" in data:
        if data["user_id"] and not db.session.get(User, data["user_id"]):
            return jsonify({"error": "Usuário não encontrado"}), 404
        task.user_id = data["user_id"]

    if "category_id" in data:
        if data["category_id"] and not db.session.get(Category, data["category_id"]):
            return jsonify({"error": "Categoria não encontrada"}), 404
        task.category_id = data["category_id"]

    if "due_date" in data:
        due_date, derr = _parse_due_date(data["due_date"])
        if derr:
            return jsonify({"error": derr}), 400
        task.due_date = due_date

    if "tags" in data:
        tags = data["tags"]
        task.tags = ",".join(tags) if isinstance(tags, list) else tags

    db.session.commit()
    return jsonify(_serialize(task)), 200


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task não encontrada"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    query = request.args.get("q", "")
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    user_id = request.args.get("user_id", "")

    tasks = Task.query
    if query:
        like = f"%{query}%"
        tasks = tasks.filter(db.or_(Task.title.like(like), Task.description.like(like)))
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        try:
            tasks = tasks.filter(Task.priority == int(priority))
        except ValueError:
            return jsonify({"error": "priority inválido"}), 400
    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except ValueError:
            return jsonify({"error": "user_id inválido"}), 400

    return jsonify([t.to_dict() for t in tasks.all()]), 200


def task_stats():
    counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    total = sum(counts.values())
    done = counts.get("done", 0)
    overdue = Task.query.filter(
        Task.due_date.isnot(None),
        Task.status.notin_(["done", "cancelled"]),
        Task.due_date < now_utc(),
    ).count()

    stats = {
        "total": total,
        "pending": counts.get("pending", 0),
        "in_progress": counts.get("in_progress", 0),
        "done": done,
        "cancelled": counts.get("cancelled", 0),
        "overdue": overdue,
        "completion_rate": round((done / total) * 100, 2) if total > 0 else 0,
    }
    return jsonify(stats), 200
