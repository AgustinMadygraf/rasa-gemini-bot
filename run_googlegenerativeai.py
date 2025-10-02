"""
Path: run_googlegenerativeai.py
"""

import traceback
from flask import Flask, request, jsonify
from collections import defaultdict

from src.infrastructure.google_generative_ai.gemini_service import GeminiService

app = Flask(__name__)
gemini = GeminiService(instructions_json_path="src/infrastructure/google_generative_ai/system_instructions.json")

# Memoria simple en RAM: {sender_id: [mensajes]}
conversation_memory = defaultdict(list)

@app.route("/webhooks/rest/webhook", methods=["POST"])
def rasa_compatible_webhook():
    """
    Endpoint compatible con el API REST de Rasa.
    Espera: {"sender": "user", "message": "texto"}
    Devuelve: [{"recipient_id": "user", "text": "respuesta"}]
    """
    try:
        data = request.get_json()
        print("Datos recibidos (Rasa compatible):", data)
        prompt = data.get("message", "")
        sender = data.get("sender", "user")

        # Guardar el mensaje del usuario en la memoria
        conversation_memory[sender].append(f"Usuario: {prompt}")

        # Construir historial para enviar al modelo (últimos 10 mensajes)
        history = "\n".join(conversation_memory[sender][-10:])

        # Opcional: puedes agregar instrucciones de sistema aquí
        prompt_with_history = f"{history}\nGemini:"

        response_text = gemini.get_response(prompt_with_history)

        # Guardar la respuesta del bot en la memoria
        conversation_memory[sender].append(f"Gemini: {response_text}")

        print("Respuesta generada:", response_text)
        return jsonify([{"recipient_id": sender, "text": response_text}])
    except (KeyError, TypeError, ValueError) as e:
        print("Error en endpoint /webhooks/rest/webhook:", e)
        traceback.print_exc()
        return jsonify([{"recipient_id": "user", "text": f"[Error: {e}]"}]), 500

if __name__ == "__main__":
    app.run(port=5005, debug=True)
