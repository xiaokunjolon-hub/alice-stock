"""统一审计日志工具（stock → 写入大系统库 audit_log 表）"""
import os
import sqlite3

from flask import request, current_app


def _db_path():
    path = current_app.config.get('WORKFLOW_DB_PATH', '')
    if path and os.path.exists(path):
        return path
    return '/opt/alice-workflow/instance/alice_jewelry.db'


def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', '') or request.remote_addr or ''
    return ip.split(',')[0].strip()


def log_action(username, action, target='', detail=''):
    """写入一条审计日志（system=stock）"""
    try:
        conn = sqlite3.connect(_db_path(), timeout=5)
        conn.execute(
            "INSERT INTO audit_log (system, username, action, target, detail, ip_address) "
            "VALUES (?,?,?,?,?,?)",
            ('stock', username, action, target, detail, get_client_ip())
        )
        conn.commit()
        conn.close()
    except Exception:
        # 审计失败绝不影响业务
        current_app.logger.exception('审计日志写入失败')
