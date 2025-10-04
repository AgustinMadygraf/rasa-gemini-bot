"""
Path: src/interface_adapter/presenters/gemini_presenter.py
"""

from src.entities.gemini_response import GeminiResponse

class GeminiPresenter:
    "Presentador que transforma GeminiResponse a formatos específicos de frameworks."
    @staticmethod
    def to_rasa_response(gemini_response: GeminiResponse, recipient_id: str):
        """
        Transforma GeminiResponse a una lista de dicts compatible con Rasa REST.
        """
        response = {
            "recipient_id": recipient_id,
            "text": gemini_response.text
        }
        # Solo incluye la transcripción si existe
        if gemini_response.audio_transcription:
            response["audio_transcription"] = gemini_response.audio_transcription
        return [response]
    