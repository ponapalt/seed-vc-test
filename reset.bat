@echo off
if exist ".\runs" (
    rd /s /q ".\runs"
    echo "model directory deleted. reset complete."
) else (
    echo "model directory not found."
)

if exist ".\venv" (
    rd /s /q ".\venv"
    echo "venv directory deleted. reset complete."
) else (
    echo "venv directory not found."
)

git reset --hard origin/main

pause