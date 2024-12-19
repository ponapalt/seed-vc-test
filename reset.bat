@echo off
if exist ".\runs\model" (
    rd /s /q ".\runs\model"
    echo "model directory deleted. reset complete."
) else (
    echo "model directory not found."
)
pause