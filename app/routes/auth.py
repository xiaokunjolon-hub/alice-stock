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
JWT_EXPIRY_HOURS = 8


def _decode_jwt():
    """解析 alice_token Cookie，返回 payload 或 None"""
    token = request.cookies.get('alice_token')
    if not token:
        return None
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def is_safe_redirect(target):
    """校验重定向目标是否安全（仅允许相对路径或本域名）"""
    host = urlparse(request.host_url)
    ref = urlparse(urljoin(request.host_url, target))
    return not ref.netloc or ref.netloc == host.netloc


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    # SSO 自动登录：检测 alice_token JWT Cookie
    if request.method == 'GET':
        payload = _decode_jwt()
        if payload and payload.get('username'):
            username = payload['username']
            # 从库存系统权限表查用户
            stock_user = StockUser.query.filter_by(username=username, is_active=True).first()
            if stock_user:
                login_user(stock_user)
                return redirect(url_for('main.dashboard'))

            # 如果权限表里没有，但 SSO 有效，提示
            if payload.get('user_id'):
                flash('您的账号尚未开通库存系统权限，请联系管理员', 'warning')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('请输入用户名和密码', 'warning')
            return render_template('auth/login.html')

        # 尝试验证大系统用户库
        user_valid = _verify_workflow_user(username, password)
        if not user_valid:
            flash('账号或密码错误，或账号已被禁用', 'danger')
            return render_template('auth/login.html')

        # 查库存系统权限表
        stock_user = StockUser.query.filter_by(username=username, is_active=True).first()
        if not stock_user:
            flash('您的账号尚未开通库存系统权限，请联系管理员', 'warning')
            return render_template('auth/login.html')

        login_user(stock_user)
        flash(f'欢迎，{username}', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已安全退出', 'info')
    return redirect(url_for('auth.login'))


def _verify_workflow_user(username, password):
    """验证大系统用户（只读查询）"""
    import sqlite3
    from flask import current_app

    db_path = current_app.config.get('WORKFLOW_DB_PATH', '')
    if not db_path or not os.path.exists(db_path):
        return False

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT password_hash, is_active FROM users WHERE username = ?",
            (username,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return False

        password_hash, is_active = row
        if not is_active:
            return False

        from werkzeug.security import check_password_hash
        return check_password_hash(password_hash, password)
    except Exception:
        return False
