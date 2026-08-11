"""Notification service — pulls email/SMS/push side effects out of the controllers.

Uses structured logging instead of print(). In a real system these methods would call
an email/SMS/push provider; here they log, keeping the concern isolated and testable.
"""
import logging

logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: seu pedido foi recebido")
    logger.info("PUSH: novo pedido recebido pelo sistema")


def notificar_status_pedido(pedido_id, status):
    if status == "aprovado":
        logger.info("NOTIFICAÇÃO: pedido %s aprovado — preparar envio", pedido_id)
    elif status == "cancelado":
        logger.info("NOTIFICAÇÃO: pedido %s cancelado — devolver estoque", pedido_id)
