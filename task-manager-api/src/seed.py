"""Populate the database with initial data. Run: python src/seed.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import timedelta  # noqa: E402

from app import create_app  # noqa: E402
from database import db  # noqa: E402
from models import Category, Task, User  # noqa: E402
from utils.timeutils import now_utc  # noqa: E402


def seed_data():
    app = create_app()
    with app.app_context():
        Task.query.delete()
        User.query.delete()
        Category.query.delete()
        db.session.commit()

        users = [
            ("João Silva", "joao@email.com", "1234", "admin"),
            ("Maria Santos", "maria@email.com", "abcd", "user"),
            ("Pedro Oliveira", "pedro@email.com", "pass", "manager"),
        ]
        user_objs = []
        for name, email, pwd, role in users:
            u = User()
            u.name = name
            u.email = email
            u.set_password(pwd)
            u.role = role
            db.session.add(u)
            user_objs.append(u)
        db.session.commit()

        categories = [
            ("Backend", "Tarefas de backend", "#3498db"),
            ("Frontend", "Tarefas de frontend", "#2ecc71"),
            ("DevOps", "Tarefas de infraestrutura", "#e74c3c"),
            ("Bug", "Correção de bugs", "#e67e22"),
        ]
        cat_objs = []
        for name, desc, color in categories:
            c = Category()
            c.name = name
            c.description = desc
            c.color = color
            db.session.add(c)
            cat_objs.append(c)
        db.session.commit()

        u1, u2, u3 = user_objs
        c1, c2, c3, c4 = cat_objs
        tasks_data = [
            {"title": "Implementar autenticação JWT", "description": "Adicionar autenticação real com JWT", "status": "pending", "priority": 1, "user_id": u1.id, "category_id": c1.id, "due_date": now_utc() - timedelta(days=3)},
            {"title": "Criar tela de login", "description": "Tela de login responsiva", "status": "in_progress", "priority": 2, "user_id": u2.id, "category_id": c2.id, "due_date": now_utc() + timedelta(days=5)},
            {"title": "Configurar CI/CD", "description": "Pipeline com GitHub Actions", "status": "done", "priority": 2, "user_id": u3.id, "category_id": c3.id, "tags": "devops,ci,github"},
            {"title": "Corrigir bug no filtro de busca", "description": "Filtro não funciona com caracteres especiais", "status": "pending", "priority": 1, "user_id": u1.id, "category_id": c4.id, "due_date": now_utc() - timedelta(days=1)},
            {"title": "Adicionar paginação na API", "description": "Endpoints retornam todos os registros", "status": "pending", "priority": 3, "user_id": u1.id, "category_id": c1.id, "due_date": now_utc() + timedelta(days=10)},
            {"title": "Escrever testes unitários", "description": "Cobertura mínima de 80%", "status": "pending", "priority": 2, "user_id": u2.id, "category_id": c1.id},
            {"title": "Documentar API com Swagger", "description": "Gerar documentação automática", "status": "cancelled", "priority": 4, "user_id": u3.id, "category_id": c1.id},
            {"title": "Refatorar models", "description": "Melhorar organização dos models", "status": "in_progress", "priority": 3, "user_id": u2.id, "category_id": c1.id, "tags": "refactor,tech-debt"},
            {"title": "Configurar monitoramento", "description": "Prometheus + Grafana", "status": "pending", "priority": 4, "user_id": u3.id, "category_id": c3.id, "due_date": now_utc() + timedelta(days=20)},
            {"title": "Melhorar validações de input", "description": "Usar marshmallow ou pydantic", "status": "pending", "priority": 3, "user_id": u1.id, "category_id": c1.id, "tags": "improvement,validation"},
        ]
        for td in tasks_data:
            t = Task()
            t.title = td["title"]
            t.description = td["description"]
            t.status = td["status"]
            t.priority = td["priority"]
            t.user_id = td["user_id"]
            t.category_id = td["category_id"]
            if "due_date" in td:
                t.due_date = td["due_date"]
            if "tags" in td:
                t.tags = td["tags"]
            db.session.add(t)
        db.session.commit()

        print("Seed concluído com sucesso!")
        print(f"  {User.query.count()} usuários")
        print(f"  {Category.query.count()} categorias")
        print(f"  {Task.query.count()} tasks")


if __name__ == "__main__":
    seed_data()
