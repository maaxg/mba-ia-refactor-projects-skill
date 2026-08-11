"""Pedido data access — atomic order creation, JOIN-based reads (no N+1)."""
from config.exceptions import ValidationError
from models.db import get_connection


def criar(usuario_id, itens):
    """Create an order atomically: validate stock, insert order + items, decrement stock.

    Everything runs in a single transaction; any failure rolls back (no partial writes).
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("BEGIN")

        total = 0
        preparados = []
        for item in itens:
            produto = cur.execute(
                "SELECT id, nome, preco, estoque FROM produtos WHERE id = ?",
                (item["produto_id"],),
            ).fetchone()
            if produto is None:
                raise ValidationError(f"Produto {item['produto_id']} não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
            total += produto["preco"] * item["quantidade"]
            preparados.append((item, produto["preco"]))

        cur.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cur.lastrowid

        for item, preco_unitario in preparados:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
                "VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], preco_unitario),
            )
            cur.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        conn.commit()
        return {"pedido_id": pedido_id, "total": total}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _montar_pedidos(rows_pedidos, rows_itens):
    itens_por_pedido = {}
    for it in rows_itens:
        itens_por_pedido.setdefault(it["pedido_id"], []).append({
            "produto_id": it["produto_id"],
            "produto_nome": it["produto_nome"] if it["produto_nome"] else "Desconhecido",
            "quantidade": it["quantidade"],
            "preco_unitario": it["preco_unitario"],
        })
    return [
        {
            "id": p["id"],
            "usuario_id": p["usuario_id"],
            "status": p["status"],
            "total": p["total"],
            "criado_em": p["criado_em"],
            "itens": itens_por_pedido.get(p["id"], []),
        }
        for p in rows_pedidos
    ]


def _carregar_itens(conn, pedido_ids):
    if not pedido_ids:
        return []
    placeholders = ",".join("?" for _ in pedido_ids)
    return conn.execute(
        f"SELECT ip.*, p.nome AS produto_nome FROM itens_pedido ip "
        f"LEFT JOIN produtos p ON p.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders})",
        pedido_ids,
    ).fetchall()


def listar_por_usuario(usuario_id):
    conn = get_connection()
    try:
        pedidos = conn.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()
        itens = _carregar_itens(conn, [p["id"] for p in pedidos])
        return _montar_pedidos(pedidos, itens)
    finally:
        conn.close()


def listar_todos():
    conn = get_connection()
    try:
        pedidos = conn.execute("SELECT * FROM pedidos").fetchall()
        itens = _carregar_itens(conn, [p["id"] for p in pedidos])
        return _montar_pedidos(pedidos, itens)
    finally:
        conn.close()


def atualizar_status(pedido_id, novo_status):
    conn = get_connection()
    try:
        conn.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        conn.commit()
        return True
    finally:
        conn.close()


def estatisticas():
    """Single aggregate query — replaces five separate COUNT/SUM round-trips."""
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS total_pedidos,
                COALESCE(SUM(total), 0) AS faturamento,
                SUM(CASE WHEN status = 'pendente'  THEN 1 ELSE 0 END) AS pendentes,
                SUM(CASE WHEN status = 'aprovado'  THEN 1 ELSE 0 END) AS aprovados,
                SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados
            FROM pedidos
            """
        ).fetchone()
        return {
            "total_pedidos": row["total_pedidos"],
            "faturamento": row["faturamento"],
            "pendentes": row["pendentes"] or 0,
            "aprovados": row["aprovados"] or 0,
            "cancelados": row["cancelados"] or 0,
        }
    finally:
        conn.close()
