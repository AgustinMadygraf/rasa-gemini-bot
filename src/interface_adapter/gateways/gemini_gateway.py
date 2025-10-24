"""
Path: src/interface_adapter/gateways/gemini_gateway.py
"""

from src.entities.gemini_responder import GeminiResponder
from src.entities.system_instructions import SystemInstructions

class GeminiGateway(GeminiResponder):
    """
    Gateway para interactuar con un servicio de modelo generativo (Gemini).
    No depende de infrastructure, solo de la entidad.
    """
    def __init__(self, service):
        """
        :param service: Instancia de un servicio que implemente get_response(prompt, system_instructions)
        """
        self.service = service

    def get_response(self, prompt, system_instructions: SystemInstructions = None):
        """
        Llama al servicio subyacente para obtener una respuesta.
        :param prompt: str, el mensaje del usuario.
        :param system_instructions: SystemInstructions | None, instrucciones de sistema como entidad.
        """
        # Si se pasa una instancia de SystemInstructions, extrae el contenido
        instructions_content = (
            str(system_instructions) if isinstance(system_instructions, SystemInstructions) else system_instructions
        )
        return self.service.get_response(prompt, instructions_content)
