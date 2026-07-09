"""大系统数据库只读查询工具"""
import sqlite3
import os
from flask import current_app


def _get_db_path():
    """获取大系统数据库路径，优先环境变量，否则用 config 默认值"""
    return current_app.config.get('WORKFLOW_DB_PATH', '')


def _connect():
    """连接大系统数据库（只读）"""
    db_path = _get_db_path()
    if not db_path or not os.path.exists(db_path):
        return None
    conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def query_one(sql, params=()):
    """查询单条记录，返回 dict 或 None"""
    conn = _connect()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def query_all(sql, params=()):
    """查询多条记录，返回 list[dict]"""
    conn = _connect()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def query_count(sql, params=()):
    """查询 COUNT，返回整数"""
    conn = _connect()
    if not conn:
        return 0
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


# ── 业务查询 ──────────────────────────────────────────────

def get_order(order_id):
    """获取单个订单详情"""
    return query_one("""
        SELECT o.*, c.name as customer_name, c.phone as customer_phone,
               u.real_name as creator_name, u.username as creator_username
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        LEFT JOIN users u ON o.created_by = u.id
        WHERE o.id = ?
    """, (order_id,))


def search_orders(search='', status='', page=1, per_page=30):
    """搜索订单列表"""
    where = []
    params = []

    if search:
        where.append("(o.custom_order_no LIKE ? OR o.title LIKE ? OR c.name LIKE ?)")
        like = f'%{search}%'
        params.extend([like, like, like])

    if status:
        where.append("o.status = ?")
        params.append(status)

    where_clause = ('WHERE ' + ' AND '.join(where)) if where else ''

    # 总数
    total = query_count(f"""
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        {where_clause}
    """, tuple(params))

    # 分页
    offset = (page - 1) * per_page
    rows = query_all(f"""
        SELECT o.id, o.custom_order_no, o.title, o.status, o.design_type,
               o.material, o.ring_size, o.necklace_length, o.wrist_size,
               o.created_at, o.completed_at,
               c.name as customer_name, c.phone as customer_phone
        FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.id
        {where_clause}
        ORDER BY o.created_at DESC
        LIMIT ? OFFSET ?
    """, tuple(params + [per_page, offset]))

    return rows, total


def get_order_stones(order_id):
    """获取订单关联的石头"""
    return query_all("""
        SELECT * FROM stones WHERE order_id = ?
        ORDER BY id
    """, (order_id,))


# ── 状态显示映射（跟大系统一致）────────────────────────────

ORDER_STATUS_MAP = {
    'draft': '草稿',
    'pending_design': '待接单',
    'designing': '设计中',
    'design_confirmed': '设计已确认',
    'pending_stone_measurement': '待丈量',
    'stone_measured': '已丈量',
    'in_production': '制作中',
    'pending_sales_receipt': '待店员确认',
    'sales_received': '店员已收到',
    'delivered': '已交付顾客',
    'completed': '已完成',
    'cancelled': '已取消',
}

DESIGN_TYPE_MAP = {
    'ring': '戒指', 'necklace': '项链', 'pendant': '吊坠',
    'earrings': '耳饰', 'bracelet': '手链/手镯',
    'brooch': '胸针', 'set': '套装', 'other': '其他',
}

STONE_TYPE_MAP = {
    'diamond': '钻石', 'gemstone': '彩色宝石',
    'pearl': '珍珠', 'coral': '珊瑚', 'jade': '翡翠/玉石', 'other': '其他',
}


def status_display(status):
    return ORDER_STATUS_MAP.get(status, status)


def design_type_display(dt):
    return DESIGN_TYPE_MAP.get(dt, dt or '—')


def stone_type_display(st):
    return STONE_TYPE_MAP.get(st, st or '—')
