"""
Path: actions/actions.py
"""

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ValidateInstalarRasaForm(FormValidationAction):
    " Validates the instalar_rasa_form form"
    def name(self) -> Text:
        return "validate_instalar_rasa_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return ["git_instalado"]

    async def extract_git_instalado(
        self, _dispatcher: CollectingDispatcher, tracker: Tracker, _domain: Dict
    ) -> Dict[Text, Any]:
        " Extrae el valor del slot git_instalado basado en la intención del usuario"
        intent = tracker.latest_message.get("intent", {}).get("name")

        if intent == "afirmar" or intent == "informar_git":
            # Verificar si el mensaje contiene indicios de que SÍ tiene Git
            text = tracker.latest_message.get("text", "").lower()
            if any(word in text for word in ["sí", "si", "tengo", "instalado", "ya", "claro"]):
                return {"git_instalado": "si"}

        if intent == "negar":
            return {"git_instalado": "no"}

        # Si menciona Git específicamente
        text = tracker.latest_message.get("text", "").lower()
        if "git" in text:
            if any(word in text for word in ["no", "nunca", "falta", "aún no", "todavía no"]):
                return {"git_instalado": "no"}
            else:
                return {"git_instalado": "si"}

        return {}

    async def validate_git_instalado(
        self,
        slot_value: Any,
        _dispatcher: CollectingDispatcher,
        _tracker: Tracker,
        _domain: DomainDict,
    ) -> Dict[Text, Any]:
        " Valida el valor del slot git_instalado "
        return {"git_instalado": slot_value}
