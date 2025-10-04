"""
Path: src/entities/gemini_response.py
"""

class GeminiResponse:
    "Entidad que representa la respuesta del bot Gemini, incluyendo texto y transcripción de audio (opcional)."
    def __init__(self, text: str, audio_transcription: str = None):
        self.text = text
        self.audio_transcription = audio_transcription

    def to_dict(self):
        "Convierte la respuesta a un diccionario."
        return {
            "text": self.text,
            "audio_transcription": self.audio_transcription
        }
