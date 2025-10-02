"""
Servidor FastAPI para Gemini Bot.
"""

from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.shared.logger import get_logger
from src.shared.config import get_config
from src.infrastructure.google_generative_ai.gemini_service import GeminiService

config = get_config()
logger = get_logger("fastapi-app")

instructions_path = config.get("SYSTEM_INSTRUCTIONS_PATH")

app = FastAPI()
gemini = GeminiService(instructions_json_path=instructions_path)

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

        response_text = gemini.get_response(prompt_with_history)

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
