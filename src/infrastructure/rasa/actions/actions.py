"""
Path: src/infrastructure/rasa/actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from src.shared.logger import get_logger

from src.use_cases.validar_instalacion_rasa import ValidarInstalacionRasaUseCase

# Inicializar el logger
logger = get_logger(__name__)

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
            # Common affirmative/negative cues (cover natural variants like 'no lo tengo instalado aún')
            affirmative_cues = ["sí", "si", "tengo", "descargado", "ya", "lo tengo", "ya lo tengo", "lo descargué", "lo descargue", "ya lo descargué", "ya lo descargue"]
            negative_cues = ["no lo tengo", "no lo tengo instalado", "no tengo", "aún no", "aun no", "todavía no", "todavia no", "no lo instalé", "no lo instale", "nunca", "falta descargar", "no está", "no esta"]

            # Intent-based quick paths
            if intent == "afirmar":
                logger.debug("Intent 'afirmar' detected while extracting proyecto_descargado")
                return {"proyecto_descargado": "si"}

            if intent == "negar":
                logger.debug("Intent 'negar' detected while extracting proyecto_descargado")
                return {"proyecto_descargado": "no"}

            # Text-based checks (more permissive)
            normalized = text_l.strip()
            # exact short answers
            if normalized in ["si", "sí"]:
                logger.debug("Short affirmative answer detected: %s", text)
                return {"proyecto_descargado": "si"}
            if normalized in ["no", "n" , "nope"]:
                logger.debug("Short negative answer detected: %s", text)
                return {"proyecto_descargado": "no"}

            # contains checks
            if any(cue in text_l for cue in negative_cues):
                logger.debug("Negative cue matched in text: %s -> %s", text, [c for c in negative_cues if c in text_l])
                return {"proyecto_descargado": "no"}

            if any(cue in text_l for cue in affirmative_cues):
                logger.debug("Affirmative cue matched in text: %s -> %s", text, [c for c in affirmative_cues if c in text_l])
                return {"proyecto_descargado": "si"}

            # As a last resort, map single-word answers containing 'instal' or 'descarg' heuristically
            if "instal" in text_l or "descarg" in text_l or "clon" in text_l:
                # assume it's affirmative if it contains past-tense cues like 'ya' or 'tengo'
                if any(w in text_l for w in ["ya", "tengo", "descarg", "clon", "clonado", "descargado"]):
                    logger.debug("Heuristic affirmative for text: %s", text)
                    return {"proyecto_descargado": "si"}
                # otherwise prefer negative if 'no' present
                if any(w in text_l for w in ["no", "aún", "aun", "todavía", "todavia", "nunca"]):
                    logger.debug("Heuristic negative for text: %s", text)
                    return {"proyecto_descargado": "no"}

        # Do not infer slot from generic mentions outside the form interaction
        return {}

    async def validate_proyecto_descargado(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        _domain: DomainDict,
    ) -> Dict[Text, Any]:
        "Valida el valor del slot proyecto_descargado usando el caso de uso"
        logger.debug("Validating 'proyecto_descargado' slot with value: %s active_loop=%s requested_slot=%s",
                     slot_value, tracker.active_loop, tracker.get_slot("requested_slot"))

        if not isinstance(slot_value, str):
            logger.debug("Invalid slot type for proyecto_descargado: %s", type(slot_value))
            return {"proyecto_descargado": None}

        val = slot_value.lower().strip()
        if val not in ["si", "sí", "no"]:
            logger.debug("Unrecognized value for proyecto_descargado: %s", val)
            dispatcher.utter_message(response="utter_ask_proyecto_descargado")
            return {"proyecto_descargado": None}

        proyecto = ValidarInstalacionRasaUseCase.validar_proyecto_descargado(val)
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None
        if active_loop == "instalar_rasa_form":
            git_value = tracker.get_slot("git_instalado")
            git = ValidarInstalacionRasaUseCase.validar_git_instalado(git_value if git_value else "no")
            resultado = ValidarInstalacionRasaUseCase.necesita_descarga_y_git(proyecto, git)
            logger.debug("Resultado caso de uso: %s", resultado)
            if resultado["necesita_descarga"]:
                if resultado["puede_clonar"]:
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
