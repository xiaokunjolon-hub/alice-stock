import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # 数据库表创建
    with app.app_context():
        from app import models  # noqa: F401 — 确保所有模型注册到 SQLAlchemy
        db.create_all()

    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.login_message_category = 'warning'


    def _check_workflow_user_active(username):
        """检查大系统用户是否存在且启用"""
        import sqlite3
        db_path = os.environ.get('WORKFLOW_DB_PATH', '')
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

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import StockUser
        stock_user = StockUser.query.get(int(user_id))
        if stock_user and not _check_workflow_user_active(stock_user.username):
            return None
        return stock_user

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def utility_processor():
        def status_badge(status):
            colors = {
                'in_stock': 'badge-green',
                'locked': 'badge-yellow',
                'out': 'badge-gray',
                'returned': 'badge-red',
                'display': 'badge-blue',
                'in_progress': 'badge-blue',
                'completed': 'badge-green',
                'pending_check': 'badge-yellow',
            }
            return colors.get(status, 'badge-gray')

        return dict(status_badge=status_badge)

    return app
