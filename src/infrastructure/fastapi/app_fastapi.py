"""
Path: src/infrastructure/fastapi/app_fastapi.py
"""

import os
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.logger import get_logger

logger = get_logger("fastapi-app")

def create_app(mode="GOOGLE_GEMINI"):
    """
    Crea y devuelve la aplicación FastAPI según el modo.
    """
    if mode == "ESPEJO":
        espejo_app = FastAPI()

        @espejo_app.post("/webhooks/rest/webhook")
        async def espejo_webhook(request: Request):
            data = await request.json()
            prompt = data.get("message", "")
            sender = data.get("sender", "user")
            logger.debug("Modo espejo: prompt='%s', sender='%s'", prompt, sender)
            return JSONResponse([{"recipient_id": sender, "text": prompt}])
        return espejo_app

    # --- SOLO SE EJECUTA SI NO ES ESPEJO ---
    from src.shared.config import get_config

    from src.infrastructure.google_generative_ai.gemini_service import GeminiService
    from src.infrastructure.repositories.json_instructions_repository import JsonInstructionsRepository
    from src.infrastructure.audio.local_audio_transcriber import LocalAudioTranscriber
    from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
    from src.interface_adapter.gateways.audio_transcriber_gateway import AudioTranscriberGateway
    from src.interface_adapter.controllers.gemini_controller import GeminiController
    from src.interface_adapter.presenters.gemini_presenter import GeminiPresenter
    from src.use_cases.generate_gemini_response_with_audio import GenerateGeminiResponseWithAudioUseCase
    from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase

    config = get_config()

    # Obtener ruta de instrucciones del sistema
    instructions_path = config.get("SYSTEM_INSTRUCTIONS_PATH")

    # Crear repositorio de instrucciones
    instructions_repository = JsonInstructionsRepository(instructions_path)

    # Usar el caso de uso para cargar las instrucciones
    load_instructions_use_case = LoadSystemInstructionsUseCase(instructions_repository)
    system_instructions = load_instructions_use_case.execute()

    logger.debug("Instrucciones de sistema cargadas: %s", system_instructions)

    fastapi_app = FastAPI()
    gemini_service = GeminiService(api_key=None)
    gemini = GeminiGateway(gemini_service)

    # Memoria simple en RAM: {sender_id: [mensajes]}
    conversation_memory = defaultdict(list)

    # Instanciar infraestructura de transcripción
    local_transcriber = LocalAudioTranscriber(vosk_model_path="model")
    audio_transcriber_gateway = AudioTranscriberGateway(local_transcriber)

    # Caso de uso orquestador
    generate_response_use_case = GenerateGeminiResponseWithAudioUseCase(
        gemini_responder=gemini,
        audio_transcriber=audio_transcriber_gateway
    )

    # Controlador desacoplado
    gemini_controller = GeminiController(generate_response_use_case)

    @fastapi_app.post("/webhooks/rest/webhook")
    async def rasa_compatible_webhook(request: Request):
        """
        Endpoint compatible con el API REST de Rasa.
        Ahora acepta texto o audio (multipart/form-data).
        """
        try:
            # Detectar si es multipart (audio) o JSON (texto)
            if request.headers.get("content-type", "").startswith("multipart"):
                form = await request.form()
                audio_file = form.get("audio")
                sender = form.get("sender", "user")
                prompt = form.get("message", "")
                audio_path = None
                if audio_file:
                    audio_path = f"/tmp/{audio_file.filename}"
                    with open(audio_path, "wb") as f:
                        f.write(await audio_file.read())
            else:
                data = await request.json()
                prompt = data.get("message", "")
                sender = data.get("sender", "user")
                audio_path = None

            # Guardar el mensaje del usuario en la memoria (opcional)
            conversation_memory[sender].append(f"Usuario: {prompt or '[audio]'}")

            # Construir historial para enviar al modelo (últimos 10 mensajes)
            history = "\n".join(conversation_memory[sender][-10:])
            prompt_with_history = f"{history}\nGemini:"

            # Llamar al controlador
            gemini_response = gemini_controller.handle_message(
                prompt=prompt_with_history if not audio_path else None,
                audio_file_path=audio_path,
                _sender=sender,
                system_instructions=system_instructions
            )

            # Guardar la respuesta del bot en la memoria
            conversation_memory[sender].append(f"Gemini: {gemini_response.text}")

            # Presentar la respuesta
            response = GeminiPresenter.to_rasa_response(gemini_response, sender)

            return JSONResponse(response)
        except (ValueError, KeyError, TypeError, IOError) as e:
            logger.error("Error en el webhook: %s", e)
            return JSONResponse([{"recipient_id": "user", "text": f"[Error: {e}]"}], status_code=400)

    return fastapi_app

# Exporta la app según el modo de entorno
_app_mode = os.environ.get("APP_MODE", "GOOGLE_GEMINI")
app = create_app(_app_mode)
