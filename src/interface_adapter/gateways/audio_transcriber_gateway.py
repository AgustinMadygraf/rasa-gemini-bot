"""
Path: src/interface_adapter/gateways/audio_transcriber_gateway.py
"""

from src.use_cases.audio_transcriber_use_case import AudioTranscriberUseCase

class AudioTranscriberGateway(AudioTranscriberUseCase):
    "Puerta de enlace que implementa el caso de uso de transcripción de audio."
    def __init__(self, transcriber_impl: AudioTranscriberUseCase):
        self.transcriber_impl = transcriber_impl

    def transcribe(self, audio_file_path: str):
        return self.transcriber_impl.transcribe(audio_file_path)
