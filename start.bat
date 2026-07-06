@echo off
chcp 65001 >nul
title Alice Stock - Inventory System

cd /d "%~dp0"

echo.
echo ========================================
echo   艾丽斯珠宝 · 库存管理系统
echo ========================================
echo.
echo Python:
py -3 --version
echo.
echo 服务器启动中...
echo 稍后访问 http://127.0.0.1:5004
echo 按 Ctrl+C 停止
echo.

start "" http://127.0.0.1:5004
py -3 run.py
pause
