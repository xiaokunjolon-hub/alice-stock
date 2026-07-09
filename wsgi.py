"""WSGI 入口 — Gunicorn 启动用"""
from app import create_app

app = create_app()
