"""
Path: run_transcriber.py
"""

from src.shared.logger import get_logger

from src.infrastructure.audio.local_audio_transcriber import LocalAudioTranscriber
from src.interface_adapter.controllers.audio_transcriber_controller import AudioTranscriberController

logger = get_logger("run-transcriber")

if __name__ == "__main__":
    use_case = LocalAudioTranscriber()
    controller = AudioTranscriberController(use_case)
    audio_file_path = input("Ingrese la ruta del archivo de audio: ")
    try:
        transcription = controller.transcribe_audio(audio_file_path)
        logger.info("Transcripción: %s", transcription.text)
    except FileNotFoundError as e:
        logger.error("No se encontró el archivo: %s", e)
        logger.warning("Intentando fallback: transcripción vacía.")
        logger.info("Transcripción: ")
    except PermissionError as e:
        logger.error("No se tienen permisos para acceder al archivo: %s", e)
        logger.warning("Intentando fallback: transcripción vacía.")
        logger.info("Transcripción: ")
    except OSError as e:
        logger.error("Ocurrió un error de sistema durante la transcripción: %s", e)
        logger.warning("Intentando fallback: transcripción vacía.")
        logger.info("Transcripción: ")
