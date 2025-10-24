"""
Path: actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionGeminiFallback(Action):
    def name(self) -> Text:
        return "action_gemini_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Aquí deberías importar tu gateway o servicio Gemini real
        from src.infrastructure.google_generative_ai.gemini_service import GeminiService

        user_message = tracker.latest_message.get("text", "")
        gemini_service = GeminiService()  # Usa la configuración de tu .env
        respuesta = gemini_service.get_response(user_message)
        dispatcher.utter_message(text=respuesta)
        return []
