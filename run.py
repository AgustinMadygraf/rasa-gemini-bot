"""
Punto de entrada para lanzar la aplicación FastAPI o Rasa según argumento o .env.
"""

import sys
import subprocess

from src.shared.config import get_config
from src.shared.logger_rasa_v0 import get_logger

logger = get_logger(__name__)

def main():
    " Determina el modo y lanza la aplicación correspondiente."
    logger.debug("Argumentos recibidos: %s", sys.argv)
    mode = None

    # Verifica argumento tipo mode=xxx
    for arg in sys.argv[1:]:
        if arg.startswith("mode="):
            mode = arg.split("=", 1)[1].upper()
            break
        elif arg == "--rasa":
            mode = "RASA"
            break
        elif arg == "--gemini":
            mode = "GOOGLE_GEMINI"
            break
        elif arg == "--espejo":
            mode = "ESPEJO"
            break
        else:
            logger.warning("Argumento desconocido: %s", arg)

    # Si no hay argumento, usa .env
    if not mode:
        config = get_config()
        logger.debug("Configuración cargada desde .env: %s", config)
        mode = config.get("MODE", "RASA").upper()
    logger.info("Modo seleccionado: %s", mode)

    try:
        if mode == "RASA":
            logger.info("Iniciando Rasa como subproceso...")
            subprocess.run(["rasa", "run", "--enable-api"], check=True)
        elif mode in ("GOOGLE_GEMINI", "ESPEJO"):
            logger.info("Iniciando FastAPI en modo %s...", mode)
            import os
            os.environ["APP_MODE"] = mode
            import uvicorn
            uvicorn.run(
                "src.infrastructure.fastapi.app_fastapi:app",
                host="0.0.0.0",
                port=5005,
                reload=True
            )
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
