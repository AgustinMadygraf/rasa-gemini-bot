"""
Path: src/interface_adapter/controllers/gemini_controller.py
"""

from src.use_cases.generate_gemini_response_with_audio import GenerateGeminiResponseWithAudioUseCase

class GeminiController:
    "Controlador que maneja las solicitudes para generar respuestas de Gemini, con soporte para audio."
    def __init__(self, generate_response_use_case: GenerateGeminiResponseWithAudioUseCase):
        self.generate_response_use_case = generate_response_use_case

    def handle_message(self, prompt: str = None, audio_file_path: str = None, _sender: str = "user", system_instructions: str = None):
        "Maneja un mensaje entrante, que puede ser texto o un archivo de audio."
        return self.generate_response_use_case.execute(
            prompt=prompt,
            audio_file_path=audio_file_path,
            system_instructions=system_instructions
        )
