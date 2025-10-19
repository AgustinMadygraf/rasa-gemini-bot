"""
Path: src/infrastructure/rasa/actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from src.shared.logger import get_logger

# Inicializar el logger
logger = get_logger(__name__)

class ProyectoEntity:
    "Entidad que representa el estado del proyecto"
    def __init__(self, esta_descargado: bool = False):
        self.esta_descargado = esta_descargado

    def necesita_descarga(self) -> bool:
        "Verifica si el proyecto necesita ser descargado"
        return not self.esta_descargado

class GitEntity:
    """Entidad que representa el estado de Git"""
    def __init__(self, esta_instalado: bool = False):
        self.esta_instalado = esta_instalado

    def puede_clonar(self) -> bool:
        "Verifica si Git está instalado para poder clonar repositorios"
        return self.esta_instalado

class ValidateInstalarRasaForm(FormValidationAction):
    "Validates the instalar_rasa_form form"
    def name(self) -> Text:
        return "validate_instalar_rasa_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        logger.debug("Determining required slots for instalar_rasa_form.")
        return ["proyecto_descargado", "git_instalado"]

    async def extract_proyecto_descargado(
        self, _dispatcher: CollectingDispatcher, tracker: Tracker, _domain: Dict
    ) -> Dict[Text, Any]:
        "Extrae el valor del slot proyecto_descargado basado en la intención del usuario"
        intent = tracker.latest_message.get("intent", {}).get("name")
        logger.debug("Extracting 'proyecto_descargado' slot. Detected intent: %s", intent)

        if intent == "afirmar":
            text = tracker.latest_message.get("text", "").lower()
            logger.debug("User text for afirmación: %s", text)
            if any(word in text for word in ["sí", "si", "tengo", "descargado", "ya", "claro"]):
                return {"proyecto_descargado": "si"}

        if intent == "negar":
            logger.debug("User negated having the project.")
            return {"proyecto_descargado": "no"}

        text = tracker.latest_message.get("text", "").lower()
        logger.debug("User text for proyecto_descargado: %s", text)
        if "messenger" in text or "bridge" in text or "proyecto" in text:
            if any(word in text for word in ["no", "nunca", "falta", "aún no", "todavía no"]):
                return {"proyecto_descargado": "no"}
            else:
                return {"proyecto_descargado": "si"}

        return {}

    async def validate_proyecto_descargado(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        _domain: DomainDict,
    ) -> Dict[Text, Any]:
        "Valida el valor del slot proyecto_descargado usando la entidad ProyectoEntity"
        logger.debug("Validating 'proyecto_descargado' slot with value: %s", slot_value)
        proyecto = ProyectoEntity(esta_descargado=slot_value.lower() == "si")

        if proyecto.necesita_descarga():
            git_value = tracker.get_slot("git_instalado")
            git = GitEntity(esta_instalado=git_value == "si" if git_value else False)
            logger.debug("Git installation status: %s", git.esta_instalado)

            if git.puede_clonar():
                dispatcher.utter_message(response="utter_guia_clonar_proyecto")
            else:
                dispatcher.utter_message(text="Primero necesitarás instalar Git para poder descargar el proyecto.")

        return {"proyecto_descargado": slot_value}

    async def extract_git_instalado(
        self, _dispatcher: CollectingDispatcher, tracker: Tracker, _domain: Dict
    ) -> Dict[Text, Any]:
        " Extrae el valor del slot git_instalado basado en la intención del usuario"
        intent = tracker.latest_message.get("intent", {}).get("name")
        logger.debug("Extracting 'git_instalado' slot. Detected intent: %s", intent)

        if intent == "afirmar" or intent == "informar_git":
            text = tracker.latest_message.get("text", "").lower()
            logger.debug("User text for afirmación: %s", text)
            if any(word in text for word in ["sí", "si", "tengo", "instalado", "ya", "claro"]):
                return {"git_instalado": "si"}

        if intent == "negar":
            logger.debug("User negated having Git installed.")
            return {"git_instalado": "no"}

        text = tracker.latest_message.get("text", "").lower()
        logger.debug("User text for git_instalado: %s", text)
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
        "Valida el valor del slot git_instalado"
        logger.debug("Validating 'git_instalado' slot with value: %s", slot_value)
        return {"git_instalado": slot_value}
