"""
Path: src/infrastructure/audio/local_audio_transcriber.py
"""

import os
import speech_recognition as sr
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError

from src.shared.logger import get_logger

from src.use_cases.audio_transcriber_use_case import AudioTranscriberUseCase

from src.entities.audio_transcriber import AudioTranscription
from src.infrastructure.audio.vosk.vosk_transcriber import VoskTranscriber

logger = get_logger("local-audio-transcriber")

class LocalAudioTranscriber(AudioTranscriberUseCase):
    """
    Implementación concreta del caso de uso para transcribir audio localmente usando 
    Vosk (offline) y Google (fallback).
    """

    def __init__(self, vosk_model_path: str = "model"):
        self.vosk_transcriber = VoskTranscriber(vosk_model_path)
        self.recognizer = sr.Recognizer()

    def transcribe(self, audio_file_path: str) -> AudioTranscription:
        logger.info("Iniciando transcripción para: %s", audio_file_path)
        if not os.path.isfile(audio_file_path):
            logger.error("El archivo %s no existe.", audio_file_path)
            return AudioTranscription(
                text=f"El archivo {audio_file_path} no existe.",
                source_path=audio_file_path
            )

        wav_path = audio_file_path + ".wav"
        try:
            logger.debug("Convirtiendo %s a WAV temporal: %s", audio_file_path, wav_path)
            audio = AudioSegment.from_file(audio_file_path)
            audio.export(wav_path, format="wav")
        except (FileNotFoundError, CouldntDecodeError, OSError, ValueError, TypeError) as e:
            logger.error("Error en la conversión a WAV: %s", e)
            return AudioTranscription(
                text=f"Error en la conversión: {e}",
                source_path=audio_file_path
            )

        # Intentar con Vosk (offline)
        text = None
        if self.vosk_transcriber.vosk_enabled:
            text = self.vosk_transcriber.transcribe(wav_path)

        # Si Vosk falla o no está disponible, usar Google (requiere Internet)
        if not text or (isinstance(text, str) and text.startswith("Error usando Vosk")):
            try:
                logger.info("Intentando transcripción online con Google Speech Recognition...")
                with sr.AudioFile(wav_path) as source:
                    audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language="es-ES")
                logger.info("Transcripción exitosa con Google Speech Recognition.")
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition no pudo entender el audio.")
                text = "Audio unintelligible"
            except sr.RequestError as e:
                logger.critical("No se pudo conectar con Google Speech Recognition: %s", e)
                text = f"Could not request results from Google Speech Recognition service; {e}"
            except (OSError, ValueError) as e:
                logger.error("Error usando Google Speech Recognition: %s", e)
                text = f"Error usando Google Speech Recognition: {e}"

        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
                logger.debug("Archivo temporal eliminado: %s", wav_path)
            except OSError as e:
                logger.warning("No se pudo eliminar el archivo temporal %s: %s", wav_path, e)

        transcription = AudioTranscription(text=text, source_path=audio_file_path)
        logger.info("Transcripción finalizada para %s: %s", audio_file_path, text)
        return transcription
