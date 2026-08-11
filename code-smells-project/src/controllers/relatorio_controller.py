"""Relatório controller — sales report. Discount business rules live here (not in the model)."""
from flask import jsonify

from config.constants import DISCOUNT_TIERS
from models import pedido_model


def _calcular_desconto(faturamento):
    for limiar, taxa in DISCOUNT_TIERS:
        if faturamento > limiar:
            return faturamento * taxa
    return 0


def relatorio_vendas():
    stats = pedido_model.estatisticas()
    faturamento = stats["faturamento"]
    total = stats["total_pedidos"]
    desconto = _calcular_desconto(faturamento)

    relatorio = {
        "total_pedidos": total,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total, 2) if total > 0 else 0,
    }
    return jsonify({"dados": relatorio, "sucesso": True}), 200
