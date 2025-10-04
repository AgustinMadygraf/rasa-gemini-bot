"""
Path: src/infrastructure/fastapi/app_fastapi.py
"""

from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.logger import get_logger
from src.shared.config import get_config
from src.infrastructure.google_generative_ai.gemini_service import GeminiService
from src.interface_adapter.gateways.gemini_gateway import GeminiGateway
from src.use_cases.load_system_instructions import LoadSystemInstructionsUseCase
from src.infrastructure.repositories.json_instructions_repository import JsonInstructionsRepository

config = get_config()
logger = get_logger("fastapi-app")

# Obtener ruta de instrucciones del sistema
instructions_path = config.get("SYSTEM_INSTRUCTIONS_PATH")

# Crear repositorio de instrucciones
instructions_repository = JsonInstructionsRepository(instructions_path)

# Usar el caso de uso para cargar las instrucciones
load_instructions_use_case = LoadSystemInstructionsUseCase(instructions_repository)
system_instructions = load_instructions_use_case.execute()

logger.debug("Instrucciones de sistema cargadas: %s", system_instructions)

# Inicializar servicio y gateway
app = FastAPI()
gemini_service = GeminiService(api_key=None)  # Ya no pasamos instructions_json_path
gemini = GeminiGateway(gemini_service)  # Usar el gateway

# Memoria simple en RAM: {sender_id: [mensajes]}
conversation_memory = defaultdict(list)

@app.post("/webhooks/rest/webhook")
async def rasa_compatible_webhook(request: Request):
    """
    Endpoint compatible con el API REST de Rasa.
    Espera: {"sender": "user", "message": "texto"}
    Devuelve: [{"recipient_id": "user", "text": "respuesta"}]
    """
    try:
        data = await request.json()
        prompt = data.get("message", "")
        sender = data.get("sender", "user")

        logger.info("Mensaje recibido de %s: %s", sender, prompt)

        # Guardar el mensaje del usuario en la memoria
        conversation_memory[sender].append(f"Usuario: {prompt}")

        # Construir historial para enviar al modelo (últimos 10 mensajes)
        history = "\n".join(conversation_memory[sender][-10:])

        # Opcional: puedes agregar instrucciones de sistema aquí
        prompt_with_history = f"{history}\nGemini:"

        # Usar las instrucciones de sistema cargadas por el caso de uso
        response_text = gemini.get_response(prompt_with_history, system_instructions)

        # Guardar la respuesta del bot en la memoria
        conversation_memory[sender].append(f"Gemini: {response_text}")

        logger.info("Respuesta enviada a %s: %s", sender, response_text)

        return JSONResponse([{"recipient_id": sender, "text": response_text}])
    except ValueError as e:
        logger.error("ValueError: %s", e)
        return JSONResponse([{"recipient_id": "user", "text": f"[ValueError: {e}]"}], status_code=400)
    except KeyError as e:
        logger.error("KeyError: %s", e)
        return JSONResponse([{"recipient_id": "user", "text": f"[KeyError: {e}]"}], status_code=400)
    except TypeError as e:
        logger.error("TypeError: %s", e)
        return JSONResponse([{"recipient_id": "user", "text": f"[TypeError: {e}]"}], status_code=400)
