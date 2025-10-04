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
    logger.debug("Argumentos recibidos: %s", sys.argv)
    mode = None
    # Detecta argumento de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] == "--rasa":
            mode = "RASA"
        elif sys.argv[1] == "--gemini":
            mode = "GOOGLE_GEMINI"
        elif sys.argv[1] == "--espejo":
            mode = "ESPEJO"
        else:
            logger.warning("Argumento desconocido: %s", sys.argv[1])
    # Si no hay argumento, usa .env
    if not mode:
        config = get_config()
        logger.debug("Configuración cargada desde .env: %s", config)
        mode = config.get("MODE").upper()
    logger.info("Modo seleccionado: %s", mode)

    try:
        if mode == "RASA":
            logger.info("Iniciando Rasa como subproceso...")
            subprocess.run(["rasa", "run", "--enable-api"], check=True)
        elif mode == "GOOGLE_GEMINI":
            logger.info("Iniciando FastAPI para Gemini...")
            import uvicorn
            uvicorn.run(
                "src.infrastructure.fastapi.app_fastapi:app",
                host="0.0.0.0",
                port=5005,
                reload=True
            )
        elif mode == "ESPEJO":
            logger.info("Iniciando FastAPI en modo espejo...")
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse

            app = FastAPI()

            @app.post("/webhooks/rest/webhook")
            async def espejo_webhook(request: Request):
                data = await request.json()
                prompt = data.get("message", "")
                sender = data.get("sender", "user")
                logger.debug("Modo espejo: prompt='%s', sender='%s'", prompt, sender)
                return JSONResponse([{"recipient_id": sender, "text": prompt}])

            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port=5005)
        else:
            logger.error("Modo desconocido: %s", mode)
            input("Presione Enter para salir...")
    except subprocess.CalledProcessError as e:
        logger.exception("Error al ejecutar el subproceso para el modo %s: %s", mode, e)
    except ImportError as e:
        logger.exception("Error de importación en el modo %s: %s", mode, e)
    except (OSError, RuntimeError, ValueError) as e:  # Captura errores comunes esperados
        logger.exception("Error ejecutando el modo %s: %s", mode, e)

if __name__ == "__main__":
    main()
