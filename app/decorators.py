from functools import wraps

from flask import render_template
from flask_login import current_user


def admin_required(f):
    """仅管理员可访问（看成本等敏感信息）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return render_template('403.html'), 403
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """指定角色可访问"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return render_template('403.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
