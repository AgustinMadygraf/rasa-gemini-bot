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
        text = tracker.latest_message.get("text", "") or ""
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None

        logger.debug("Extracting 'proyecto_descargado'. intent=%s requested_slot=%s active_loop=%s text=%s",
                     intent, requested_slot, active_loop, text)

        text_l = text.lower()

        # Be conservative: only extract when the form is active and the requested_slot is proyecto_descargado
        # or when the intent explicitly affirms/negates.
        if active_loop == "instalar_rasa_form" and requested_slot == "proyecto_descargado":
            if intent == "afirmar":
                if any(word in text_l for word in ["sí", "si", "tengo", "descargado", "ya", "claro"]):
                    return {"proyecto_descargado": "si"}

            if intent == "negar":
                return {"proyecto_descargado": "no"}

            # As fallback, accept explicit short answers containing si/no
            if text_l.strip() in ["si", "sí", "no", "nunca"]:
                return {"proyecto_descargado": "si"} if text_l.strip() in ["si", "sí"] else {"proyecto_descargado": "no"}

        # Do not infer slot from generic mentions outside the form interaction
        return {}

    async def validate_proyecto_descargado(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        _domain: DomainDict,
    ) -> Dict[Text, Any]:
        "Valida el valor del slot proyecto_descargado usando la entidad ProyectoEntity"
        logger.debug("Validating 'proyecto_descargado' slot with value: %s active_loop=%s requested_slot=%s",
                     slot_value, tracker.active_loop, tracker.get_slot("requested_slot"))

        # Normalize and validate conservatively
        if not isinstance(slot_value, str):
            logger.debug("Invalid slot type for proyecto_descargado: %s", type(slot_value))
            return {"proyecto_descargado": None}

        val = slot_value.lower().strip()
        if val not in ["si", "sí", "no"]:
            logger.debug("Unrecognized value for proyecto_descargado: %s", val)
            # ask again politely
            dispatcher.utter_message(response="utter_ask_proyecto_descargado")
            return {"proyecto_descargado": None}

        proyecto = ProyectoEntity(esta_descargado=(val in ["si", "sí"]))

        # Only perform side-effects (utter) if the form is active to avoid unsolicited messages
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None
        if proyecto.necesita_descarga() and active_loop == "instalar_rasa_form":
            git_value = tracker.get_slot("git_instalado")
            git = GitEntity(esta_instalado=(git_value == "si" if git_value else False))
            logger.debug("Git installation status: %s", git.esta_instalado)

            if git.puede_clonar():
                dispatcher.utter_message(response="utter_guia_clonar_proyecto")
            else:
                dispatcher.utter_message(text="Primero necesitarás instalar Git para poder descargar el proyecto.")

        return {"proyecto_descargado": "si" if proyecto.esta_descargado else "no"}

    async def extract_git_instalado(
        self, _dispatcher: CollectingDispatcher, tracker: Tracker, _domain: Dict
    ) -> Dict[Text, Any]:
        " Extrae el valor del slot git_instalado basado en la intención del usuario"
        intent = tracker.latest_message.get("intent", {}).get("name")
        text = tracker.latest_message.get("text", "") or ""
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None

        logger.debug("Extracting 'git_instalado'. intent=%s requested_slot=%s active_loop=%s text=%s",
                     intent, requested_slot, active_loop, text)

        text_l = text.lower()

        # Conservative extraction: only when the form asks for git_instalado
        if active_loop == "instalar_rasa_form" and requested_slot == "git_instalado":
            if intent in ["afirmar", "informar_git"]:
                if any(word in text_l for word in ["sí", "si", "tengo", "instalado", "ya", "claro"]):
                    return {"git_instalado": "si"}

            if intent == "negar":
                return {"git_instalado": "no"}

            if text_l.strip() in ["si", "sí", "no"]:
                return {"git_instalado": "si"} if text_l.strip() in ["si", "sí"] else {"git_instalado": "no"}

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
