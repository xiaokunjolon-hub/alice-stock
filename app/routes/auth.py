import os
from datetime import datetime, timezone, timedelta

import jwt
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse, urljoin

from app.extensions import db
from app.models import StockUser

auth_bp = Blueprint('auth', __name__)

JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'alice-jwt-secret-change-in-production')


def _decode_jwt():
    """解析 alice_token Cookie，返回 payload 或 None"""
    token = request.cookies.get('alice_token')
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def _check_workflow_user_active(username):
    """检查大系统用户是否存在且启用"""
    import sqlite3
    from flask import current_app
    db_path = current_app.config.get('WORKFLOW_DB_PATH', '')
    if not db_path or not os.path.exists(db_path):
        return True
    try:
        conn = sqlite3.connect(db_path)
        row = conn.execute(
            "SELECT is_active FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        return row is not None and row[0]
    except Exception:
        return True


@auth_bp.route('/login', methods=['GET'])
def login():
    """库存系统不处理登录，统一跳转 custom（唯一 SSO 入口）"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # SSO 自动登录：检测 alice_token JWT Cookie
    payload = _decode_jwt()
    if payload and payload.get('username'):
        username = payload['username']
        if not _check_workflow_user_active(username):
            flash('您的账号已被禁用或删除，请联系管理员', 'warning')
            return render_template('auth/login.html')
        stock_user = StockUser.query.filter_by(username=username, is_active=True).first()
        if not stock_user:
            stock_user = StockUser(username=username, role='staff', is_active=True)
            db.session.add(stock_user)
            db.session.commit()
        if stock_user:
            login_user(stock_user)
            return redirect(url_for('main.dashboard'))

    # 没有 JWT → 跳转 custom 统一登录
    next_url = request.args.get('next') or url_for('main.dashboard')
    return redirect(f'https://custom.alicexie.com/login?next=https://stock.alicexie.com{next_url}')


@auth_bp.route('/logout')
def logout():
    """登出 → 跳转 custom 统一登出"""
    if current_user.is_authenticated:
        logout_user()
    return redirect('https://custom.alicexie.com/logout?next=https://stock.alicexie.com/')
