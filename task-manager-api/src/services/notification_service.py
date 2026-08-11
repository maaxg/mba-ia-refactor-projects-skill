"""Notification service — now a real, used layer with no hardcoded credentials.

SMTP config comes from the environment; when NOTIFICATIONS_ENABLED is false (default) it logs
instead of sending, so the app is safe to run in dev/CI without a mail server.
"""
import logging
import smtplib

from config.settings import settings

logger = logging.getLogger(__name__)


def send_email(to, subject, body):
    if not settings.NOTIFICATIONS_ENABLED:
        logger.info("Notificação (dry-run) para %s: %s", to, subject)
        return True
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to, f"Subject: {subject}\n\n{body}")
        server.quit()
        return True
    except Exception:
        logger.exception("Erro ao enviar email para %s", to)
        return False


def notify_task_assigned(user, task):
    subject = f"Nova task atribuída: {task.title}"
    body = (
        f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n"
        f"Prioridade: {task.priority}\nStatus: {task.status}"
    )
    return send_email(user.email, subject, body)
