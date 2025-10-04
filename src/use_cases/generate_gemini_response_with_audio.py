"""
Path: src/use_cases/generate_gemini_response_with_audio.py
"""

from src.entities.gemini_response import GeminiResponse
from src.use_cases.audio_transcriber_use_case import AudioTranscriberUseCase

class GenerateGeminiResponseWithAudioUseCase:
    "Caso de uso para generar respuestas"

    def __init__(self, gemini_responder, audio_transcriber: AudioTranscriberUseCase = None):
        self.gemini_responder = gemini_responder
        self.audio_transcriber = audio_transcriber

    def execute(self, prompt: str = None, audio_file_path: str = None, system_instructions: str = None):
        "Genera una respuesta de Gemini, transcribiendo audio si se proporciona un archivo de audio."
        audio_transcription = None

        # Si hay audio, transcribir
        if audio_file_path and self.audio_transcriber:
            transcription_obj = self.audio_transcriber.transcribe(audio_file_path)
            audio_transcription = transcription_obj.text
            prompt = audio_transcription  # Usar la transcripción como prompt

        # Generar respuesta de Gemini
        response_text = self.gemini_responder.get_response(prompt, system_instructions)

        # Devolver entidad enriquecida
        return GeminiResponse(text=response_text, audio_transcription=audio_transcription)
