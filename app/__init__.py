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

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import StockUser
        return StockUser.query.get(int(user_id))

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
