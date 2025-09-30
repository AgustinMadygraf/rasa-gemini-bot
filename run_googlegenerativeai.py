"""
Path: run_googlegenerativeai.py
"""

from flask import Flask, request, jsonify

from src.infrastructure.google_generative_ai.gemini_service import GeminiService

app = Flask(__name__)
gemini = GeminiService(instructions_json_path="src/infrastructure/google_generative_ai/system_instructions.json")

@app.route("/generate", methods=["POST"])
def generate():
    "Genera una respuesta a partir de un prompt utilizando el servicio Gemini."
    try:
        data = request.get_json()
        print("Datos recibidos:", data)  # <-- Agrega esto
        prompt = data.get("prompt", "")
        response = gemini.get_response(prompt)
        print("Respuesta generada:", response)  # <-- Y esto
        return jsonify({"response": response})
    except (KeyError, TypeError, ValueError) as e:
        import traceback
        print("Error en endpoint /generate:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        import traceback
        print("Error inesperado en endpoint /generate:", e)
        traceback.print_exc()
        return jsonify({"error": "Unexpected error occurred."}), 500

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
        response_text = gemini.get_response(prompt)
        print("Respuesta generada:", response_text)
        return jsonify([{"recipient_id": sender, "text": response_text}])
    except Exception as e:
        import traceback
        print("Error en endpoint /webhooks/rest/webhook:", e)
        traceback.print_exc()
        return jsonify([{"recipient_id": "user", "text": f"[Error: {e}]"}]), 500

if __name__ == "__main__":
    app.run(port=5005, debug=True)
