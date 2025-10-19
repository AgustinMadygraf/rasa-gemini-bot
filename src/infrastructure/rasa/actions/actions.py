"""
Path: src/infrastructure/rasa/actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from src.shared.logger import get_logger

from src.interface_adapter.controllers.instalar_rasa_controller import InstalarRasaController
from src.interface_adapter.presenters.instalar_rasa_presenter import InstalarRasaPresenter

# Inicializar el logger
logger = get_logger(__name__)

class ValidateInstalarRasaForm(FormValidationAction):
    "Adaptador de infraestructura para el formulario instalar_rasa_form. Traduce entre la infraestructura de Rasa y la arquitectura limpia del sistema."
    def __init__(self):
        super().__init__()
        self.presenter = InstalarRasaPresenter()
        self.controller = InstalarRasaController(presenter=self.presenter)
    
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
        "Extrae el valor del slot proyecto_descargado basado en la intención del usuario. Este método queda en la capa de infraestructura por ser específico de Rasa."
        intent = tracker.latest_message.get("intent", {}).get("name")
        text = tracker.latest_message.get("text", "") or ""
        requested_slot = tracker.get_slot("requested_slot")
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None

        logger.debug("Extracting 'proyecto_descargado'. intent=%s requested_slot=%s active_loop=%s text=%s",
                     intent, requested_slot, active_loop, text)

        text_l = text.lower()

        # Be conservative: only extract when the form is active and the requested_slot is proyecto_descargado
        if active_loop == "instalar_rasa_form" and requested_slot == "proyecto_descargado":
            # Common affirmative/negative cues
            affirmative_cues = ["sí", "si", "tengo", "descargado", "ya", "lo tengo", "ya lo tengo", "lo descargué", "lo descargue"]
            negative_cues = ["no lo tengo", "no lo tengo instalado", "no tengo", "aún no", "aun no", "todavía no", "todavia no"]

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
                logger.debug("Negative cue matched in text: %s", text)
                return {"proyecto_descargado": "no"}

            if any(cue in text_l for cue in affirmative_cues):
                logger.debug("Affirmative cue matched in text: %s", text)
                return {"proyecto_descargado": "si"}

            # Last resort heuristics
            if "instal" in text_l or "descarg" in text_l or "clon" in text_l:
                if any(w in text_l for w in ["ya", "tengo", "descarg", "clon", "clonado", "descargado"]):
                    logger.debug("Heuristic affirmative for text: %s", text)
                    return {"proyecto_descargado": "si"}
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
        "Valida el valor del slot proyecto_descargado delegando al controlador."
        logger.debug("Validating 'proyecto_descargado' slot with value: %s", slot_value)

        # Delegar la validación al controlador
        result = self.controller.validar_proyecto_descargado(slot_value)

        # Procesar el resultado del controlador
        if not result["valor_valido"]:
            # Si el valor no es válido, enviar mensaje de ayuda
            dispatcher.utter_message(**result["mensaje"])
            return {"proyecto_descargado": None}  # Rasa volverá a preguntar

        # Si estamos en el formulario activo, evaluar la instalación completa
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None
        if active_loop == "instalar_rasa_form":
            git_value = tracker.get_slot("git_instalado")

            # Si ya tenemos información sobre git, evaluamos la instalación
            if git_value:
                # Evaluar la instalación completa y mostrar mensajes apropiados
                evaluacion = self.controller.evaluar_instalacion(
                    result["valor_normalizado"], 
                    git_value
                )

                # Enviar mensajes generados por el controlador
                for mensaje in evaluacion["mensajes"]:
                    dispatcher.utter_message(**mensaje)

        # Devolver el valor normalizado para el slot
        return {"proyecto_descargado": result["valor_normalizado"]}

    async def extract_git_instalado(
        self, _dispatcher: CollectingDispatcher, tracker: Tracker, _domain: Dict
    ) -> Dict[Text, Any]:
        "Extrae el valor del slot git_instalado basado en la intención del usuario. Este método queda en la capa de infraestructura por ser específico de Rasa."
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
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        _domain: DomainDict,
    ) -> Dict[Text, Any]:
        "Valida el valor del slot git_instalado delegando al controlador."
        logger.debug("Validating 'git_instalado' slot with value: %s", slot_value)

        # Para git_instalado, evaluamos la instalación completa
        if slot_value and tracker.get_slot("proyecto_descargado"):
            evaluacion = self.controller.evaluar_instalacion(
                tracker.get_slot("proyecto_descargado"),
                slot_value
            )

            # Enviar mensajes generados por el controlador
            for mensaje in evaluacion["mensajes"]:
                dispatcher.utter_message(**mensaje)

            return {"git_instalado": evaluacion["git_instalado"]}

        return {"git_instalado": slot_value}
