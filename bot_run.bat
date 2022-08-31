@echo off

call %~dp0Volna_telegram_bot\venv\Scripts\activate

cd %~dp0Volna_telegram_bot

set TOKEN=5482172881:AAFSPNY5z8VDxwGa9lmsXU9iC5l8qf9Q6CU

python bot_telegram.py

pause