"""
Punto de entrada para lanzar la aplicación FastAPI o Rasa según argumento o .env.
"""

import sys
import subprocess
import os
from pathlib import Path

from src.shared.config import get_config
from src.shared.logger import get_logger

logger = get_logger(__name__)

def main():
    " Determina el modo y lanza la aplicación correspondiente."
    logger.debug("Argumentos recibidos: %s", sys.argv)
    mode = None
    train_model = False

    # Verifica argumento tipo mode=xxx o --train
    for arg in sys.argv[1:]:
        if arg.startswith("mode="):
            mode = arg.split("=", 1)[1].upper()
        elif arg == "--rasa":
            mode = "RASA"
        elif arg == "--gemini":
            mode = "GOOGLE_GEMINI"
        elif arg == "--espejo":
            mode = "ESPEJO"
        elif arg == "--train":
            train_model = True
        else:
            logger.warning("Argumento desconocido: %s", arg)

    # Si no hay argumento, usa .env
    if not mode and not train_model:
        config = get_config()
        logger.debug("Configuración cargada desde .env: %s", config)
        mode = config.get("MODE", "RASA").upper()
    
    # Nueva ruta para los archivos de Rasa
    rasa_dir = Path("src/infrastructure/rasa")
    
    # Entrenamiento del modelo si se especificó --train
    if train_model:
        logger.info("Iniciando entrenamiento de Rasa...")
        # Cambiar al directorio de Rasa para el entrenamiento
        original_dir = os.getcwd()
        os.chdir(rasa_dir)
        
        try:
            subprocess.run(["rasa", "train"], check=True)
            logger.info("Entrenamiento completado exitosamente.")
        except subprocess.CalledProcessError as e:
            logger.exception("Error durante el entrenamiento de Rasa: %s", e)
        finally:
            # Volver al directorio original después del entrenamiento
            os.chdir(original_dir)
            
        if not mode:  # Si solo se pidió entrenar, terminamos
            return

    logger.info("Modo seleccionado: %s", mode)

    try:
        if mode == "RASA":
            logger.info("Iniciando Rasa como subproceso...")
            # Cambiar al directorio de Rasa para la ejecución
            os.chdir(rasa_dir)
            subprocess.run(["rasa", "run", "--enable-api"], check=True)
            
            # Volver al directorio original después de la ejecución
            os.chdir(Path(rasa_dir).parent.parent.parent)
        elif mode in ("GOOGLE_GEMINI", "ESPEJO"):
            logger.info("Iniciando FastAPI en modo %s...", mode)
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
