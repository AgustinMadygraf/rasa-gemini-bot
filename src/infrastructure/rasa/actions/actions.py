"""
Path: src/infrastructure/rasa/actions/actions.py
"""

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from src.shared.logger import get_logger
from src.interface_adapter.gateways.instalar_rasa_gateway import InstalarRasaGateway
from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
from src.infrastructure.google_generative_ai.gemini_service import GeminiService

from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase
from src.shared.config import get_config

# Inicializar el logger
logger = get_logger(__name__)

class ValidateInstalarRasaForm(FormValidationAction):
    "Adaptador de infraestructura para el formulario instalar_rasa_form. Traduce entre la infraestructura de Rasa y la arquitectura limpia del sistema."
    def __init__(self):
        super().__init__()
        self.gateway = InstalarRasaGateway()

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
        "Valida el valor del slot proyecto_descargado delegando al gateway."
        logger.debug("Validating 'proyecto_descargado' slot with value: %s", slot_value)

        # Delegar la validación al gateway
        result = self.gateway.validar_proyecto_descargado(slot_value)

        # Procesar el resultado
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
                evaluacion = self.gateway.evaluar_instalacion(
                    result["valor_normalizado"],
                    git_value
                )

                # Enviar mensajes generados
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
        "Valida el valor del slot git_instalado delegando al gateway."
        logger.debug("Validating 'git_instalado' slot with value: %s", slot_value)

        # Para git_instalado, evaluamos la instalación completa
        if slot_value and tracker.get_slot("proyecto_descargado"):
            evaluacion = self.gateway.evaluar_instalacion(
                tracker.get_slot("proyecto_descargado"),
                slot_value
            )

            # Enviar mensajes generados
            for mensaje in evaluacion["mensajes"]:
                dispatcher.utter_message(**mensaje)

            return {"git_instalado": evaluacion["git_instalado"]}

        return {"git_instalado": slot_value}


class ActionProvideNextSteps(Action):
    """Proporciona instrucciones específicas basadas en el estado de los slots después de completar el formulario."""

    def __init__(self):
        super().__init__()
        self.gateway = InstalarRasaGateway()

    def name(self) -> Text:
        return "action_provide_next_steps"

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        proyecto_descargado = (tracker.get_slot("proyecto_descargado") or "no").lower()
        git_instalado = (tracker.get_slot("git_instalado") or "no").lower()

        logger.debug("action_provide_next_steps: proyecto_descargado=%s git_instalado=%s",
                     proyecto_descargado, git_instalado)

        # Si no tiene Git instalado -> sugerir instalar y cómo verificar
        if git_instalado not in ["si", "sí"]:
            dispatcher.utter_message(response="utter_install_git")
            dispatcher.utter_message(response="utter_check_git_installed")
            return []

        # Si tiene Git pero no el proyecto -> instruir clonación
        if proyecto_descargado not in ["si", "sí"]:
            dispatcher.utter_message(response="utter_guia_clonar_proyecto")
            return []

        # Si tiene ambos -> continuar con Rasa
        dispatcher.utter_message(response="utter_continue_with_rasa")
        return []


class ActionGeminiFallback(Action):
    """Fallback avanzado: delega la respuesta a Gemini cuando Rasa no tiene suficiente confianza."""

    def __init__(self):
        super().__init__()
        # Carga instrucciones de sistema desde JSON si está configurado
        config = get_config()
        instructions_path = config.get("SYSTEM_INSTRUCTIONS_PATH")
        instructions = None
        if instructions_path:
            # Importar el repositorio JSON y pasarlo al caso de uso
            from src.infrastructure.repositories.json_instructions_repository import JsonInstructionsRepository
            instructions_repository = JsonInstructionsRepository(json_path=instructions_path)
            instructions = LoadSystemInstructionsUseCase(instructions_repository).execute()
        self.gemini = GeminiGateway(
            GeminiService(api_key=config.get("GOOGLE_GEMINI_API_KEY"), instructions_json_path=instructions_path)
        )
        self.system_instructions = instructions

    def name(self) -> Text:
        return "action_gemini_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Detectar contexto y construir prompt más completo para Gemini
        events = tracker.events or []
        history = []
        for e in events:
            if e.get("event") == "user":
                txt = e.get("text") or ""
                history.append(f"Usuario: {txt}")
            elif e.get("event") == "bot":
                # bot puede haber utters sin 'text' si usa response templates
                txt = e.get("text") or ""
                if not txt:
                    # intentar extraer el template si existe
                    metadata = e.get("metadata") or {}
                    txt = metadata.get("template", "")
                if txt:
                    history.append(f"Bot: {txt}")

        # Tomar los últimos N turnos (pares user+bot) para mantener contexto
        max_turns = 10
        prompt_history = "\n".join(history[-max_turns:])

        # Incluir información de slots relevantes y active_loop
        slot_info = {k: tracker.get_slot(k) for k in tracker.slots.keys()} if hasattr(tracker, "slots") else {}
        active_loop = tracker.active_loop.get("name") if tracker.active_loop else None

        # Construir prompt final para Gemini
        last_user = tracker.latest_message.get("text", "") or ""
        prompt_parts = ["Actúa como el asistente MadyBot. Usa el historial de conversación y responde de forma breve y útil."]
        if self.system_instructions:
            prompt_parts.append(f"Instrucciones del sistema: {self.system_instructions}")
        prompt_parts.append("Historial:")
        prompt_parts.append(prompt_history)
        prompt_parts.append(f"Último mensaje de usuario: {last_user}")
        prompt_parts.append(f"Slots: {slot_info}")
        prompt_parts.append(f"Active loop: {active_loop}")

        prompt = "\n".join([p for p in prompt_parts if p])

        logger.debug("ActionGeminiFallback invoked. intent=%s latest_text=%s active_loop=%s slots=%s history_len=%d",
                     tracker.latest_message.get("intent", {}).get("name"),
                     last_user,
                     active_loop,
                     slot_info,
                     len(history))

        # Llamar a Gemini con manejo básico de errores/timeout
        try:
            # si el gateway provee un método async podríamos await; aquí usamos sync
            respuesta = self.gemini.get_response(prompt, self.system_instructions)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error calling Gemini service: %s", e, exc_info=True)
            dispatcher.utter_message(text="Lo siento, tuve un problema consultando el motor de respuestas. Intenta de nuevo más tarde.")
            return []

        # Enviar respuesta generada
        if respuesta:
            dispatcher.utter_message(text=respuesta)
        else:
            dispatcher.utter_message(text="No tengo una respuesta en este momento.")

        return []
