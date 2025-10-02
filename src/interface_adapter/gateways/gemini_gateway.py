"""
Path: src/interface_adapter/gateways/gemini_gateway.py
"""

from src.entities.gemini_responder import GeminiResponder

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

    def get_response(self, prompt, system_instructions=None):
        """
        Llama al servicio subyacente para obtener una respuesta.
        """
        return self.service.get_response(prompt, system_instructions)
