"""
Punto de entrada para lanzar la aplicación FastAPI o Rasa según argumento o .env.
"""

import sys
import subprocess

from src.shared.config import get_config
from src.shared.logger import get_logger

logger = get_logger(__name__)

def main():
    " Determina el modo y lanza la aplicación correspondiente."
    mode = None
    # Detecta argumento de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rasa":
            mode = "RASA"
        elif sys.argv[1] == "--gemini":
            mode = "GOOGLE_GEMINI"
    # Si no hay argumento, usa .env
    if not mode:
        config = get_config()
        mode = config.get("MODE", "RASA").upper()

    if mode == "RASA":
        # Ejecuta Rasa como subproceso
        subprocess.run(["rasa", "run", "--enable-api"], check=True)
    elif mode == "GOOGLE_GEMINI":
        import uvicorn
        uvicorn.run(
            "src.infrastructure.fastapi.app:app",
            host="0.0.0.0",
            port=5005,
            reload=True
        )
    else:
        print(f"Modo desconocido: {mode}")

if __name__ == "__main__":
    main()
