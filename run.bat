@echo off
call .\venv\Scripts\activate.bat
start rasa run --debug
start rasa run actions --debug
ngrok http 5005 --domain=unhued-tashia-beforehand.ngrok-free.app