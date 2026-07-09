"""库存系统种子数据 — 添加用户权限

用法:
    py -3 seed.py                # 列出已有用户
    py -3 seed.py <username>     # 添加为普通店员
    py -3 seed.py <username> admin  # 添加为管理员
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import StockUser


def list_users():
    users = StockUser.query.all()
    if not users:
        print("暂无权限用户")
        return
    print(f"当前库存系统权限用户 ({len(users)} 人):")
    for u in users:
        cost = "[可看成本]" if u.is_admin else "[不可看成本]"
        print(f"  {u.username:20s} {u.role_display:6s} {cost}")
    print()


def add_user(username, role='staff'):
    existing = StockUser.query.filter_by(username=username).first()
    if existing:
        existing.role = role
        existing.is_active = True
        db.session.commit()
        print(f"已更新: {username} -> {StockUser(role=role).role_display}")
    else:
        user = StockUser(username=username, role=role, is_active=True)
        db.session.add(user)
        db.session.commit()
        print(f"已添加: {username} -> {StockUser(role=role).role_display}")


app = create_app()

with app.app_context():
    if len(sys.argv) >= 2:
        role = sys.argv[2] if len(sys.argv) >= 3 else 'staff'
        if role not in ('admin', 'staff'):
            print(f"无效角色: {role}，可选: admin / staff")
            sys.exit(1)
        add_user(sys.argv[1], role)

    list_users()
    print("请在浏览器访问 http://127.0.0.1:5004")
    print("使用大系统账号登录（需先在此添加权限）")
