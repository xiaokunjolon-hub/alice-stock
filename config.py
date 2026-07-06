import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'alice-stock-dev-secret-key-change-in-production'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'instance', 'alice_stock.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 大系统用户库路径（只读，用于用户验证 + SSO）
    WORKFLOW_DB_PATH = os.environ.get('WORKFLOW_DB_PATH') or \
        os.path.join(os.path.dirname(BASEDIR), '艾丽斯珠宝定制', '大系统', 'instance', 'alice_jewelry.db')

    # 文件上传
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

    # 缩略图
    THUMBNAIL_FOLDER = os.path.join(BASEDIR, 'uploads', 'thumbnails')
    THUMBNAIL_SIZE = (400, 400)
