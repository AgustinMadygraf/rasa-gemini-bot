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
    models_dir = rasa_dir / "models"

    # Asegurarse de que el directorio de modelos exista
    os.makedirs(models_dir, exist_ok=True)

    # Entrenamiento del modelo si se especificó --train
    if train_model:
        logger.info("Iniciando entrenamiento de Rasa...")
        original_dir = os.getcwd()

        try:
            # Configurar RASA_HOME para que .rasa se cree en el subdirectorio
            os.environ["RASA_HOME"] = str(rasa_dir.absolute())

            # Construir el comando con rutas específicas
            train_cmd = [
                "rasa", "train",
                "--domain", str(rasa_dir / "domain.yml"),
                "--config", str(rasa_dir / "config.yml"),
                "--data", str(rasa_dir / "data"),
                "--out", str(models_dir)
            ]

            # Ejecutar entrenamiento con rutas específicas
            logger.info("Ejecutando: %s", " ".join(train_cmd))
            subprocess.run(train_cmd, check=True)
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
            # Configurar RASA_HOME para rutas consistentes
            os.environ["RASA_HOME"] = str(rasa_dir.absolute())

            # Buscar el modelo más reciente en el directorio de modelos personalizado
            model_files = list(models_dir.glob("*.tar.gz"))
            if model_files:
                latest_model = max(model_files, key=os.path.getctime)
                logger.info("Usando el modelo más reciente: %s", latest_model)

                # Ejecutar con el modelo específico
                run_cmd = [
                    "rasa", "run", 
                    "--enable-api",
                    "--endpoints", str(rasa_dir / "endpoints.yml"),
                    "-m", str(latest_model)
                ]
                subprocess.run(run_cmd, check=True)
            else:
                logger.error("No se encontraron modelos entrenados en %s", models_dir)
                input("Presione Enter para salir...")
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
