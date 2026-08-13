#!/usr/bin/env python3
"""alice-stock 数据库每日备份：用 SQLite backup API 安全备份，保留最近 7 天"""
import sqlite3, os, glob, time
from datetime import datetime

DB = '/opt/alice-stock/instance/alice_stock.db'
BACKUP_DIR = '/opt/alice-stock/backups'
KEEP_DAYS = 7

os.makedirs(BACKUP_DIR, exist_ok=True)
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_path = os.path.join(BACKUP_DIR, f'alice_stock_{ts}.db')

src = sqlite3.connect(DB)
dst = sqlite3.connect(backup_path)
with dst:
    src.backup(dst)
src.close()
dst.close()

# 清理超过 7 天的旧备份
cutoff = time.time() - KEEP_DAYS * 86400
removed = 0
for f in glob.glob(os.path.join(BACKUP_DIR, 'alice_stock_*.db')):
    if os.path.getmtime(f) < cutoff:
        os.remove(f)
        removed += 1

print(f'备份完成: {backup_path} ({os.path.getsize(backup_path)} bytes)' + (f', 清理 {removed} 个旧备份' if removed else ''))
