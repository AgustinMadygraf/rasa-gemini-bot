<!-- Copilot / AI agent instructions for the `rasa-gemini-bot` repo -->
# Instrucciones rápidas para agentes de IA (GitHub Copilot / Code agents)

Objetivo: permitir que un agente de código sea productivo de inmediato en este repositorio — comprender arquitectura, flujos principales, convenciones y comandos para ejecutar y depurar.

- Lenguaje principal: Python 3.8+.
- Frameworks: Rasa (Core + NLU + SDK, código organizado bajo `src/infrastructure/rasa`), FastAPI (API alternativa para usar Gemini), y Google Generative AI (cliente `google.generativeai`).

Puntos clave (rápido):

1) Arquitectura y límites de responsabilidad
  - `src/infrastructure/fastapi/app_fastapi.py`: aplicación HTTP que expone un webhook compatible con Rasa REST. Soporta modo `ESPEJO` (eco) y `GOOGLE_GEMINI` (llamadas al modelo). Ejemplo: la función `create_app(mode)` construye dependencias: `GeminiService` <- `GeminiGateway` <- uso en endpoints.
  - `src/infrastructure/google_generative_ai/gemini_service.py`: cliente concreto que usa `google.generativeai`. Requiere la variable de entorno `GOOGLE_GEMINI_API_KEY`. Provee `get_response(prompt, system_instructions)`.
  - `src/interface_adapter/gateways/gemini_gateway.py`: pequeña capa que adapta la entidad `SystemInstructions` a la API del servicio.
  - `src/use_cases/load_system_instructions.py` y `src/infrastructure/repositories/json_instructions_repository.py`: caso de uso y repositorio para cargar instrucciones de sistema (JSON). El `FastAPI` construye estas piezas al iniciar.
  - `run.py`: orquestador de ejecución. Detecta `mode` (RASA, GOOGLE_GEMINI, ESPEJO), admite `--train` para entrenar Rasa con rutas personalizadas en `src/infrastructure/rasa` y configura `RASA_HOME` para aislar artefactos.

2) Flujo de datos relevante
  - Mensajes entrantes llegan a `/webhooks/rest/webhook` con body {"sender":..., "message":...}. FastAPI mantiene una memoria en RAM por sender (lista de strings) y concatena los últimos 10 mensajes como historial antes de llamar a Gemini.
  - GeminiService puede prefijar instrucciones del sistema (JSON) al prompt. Es cargado vía `LoadSystemInstructionsUseCase` usando `SYSTEM_INSTRUCTIONS_PATH` (env).

3) Variables de entorno y config
  - `SYSTEM_INSTRUCTIONS_PATH` — ruta al JSON con instrucciones de sistema usadas por Gemini.
  - `GOOGLE_GEMINI_API_KEY` — obligatorio para usar `GeminiService`.
  - `GOOGLE_GEMINI_MODEL` — nombre del modelo (por defecto `models/gemini-2.5-flash` en `get_config`).
  - `MODE` — por defecto `RASA`; `run.py` y `app_fastapi.py` respetan esta variable.

4) Comandos y workflows (cómo ejecutar y depurar)
  - Ejecutar la app en modo FastAPI (local): `python run.py mode=GOOGLE_GEMINI` (o `--gemini`). Esto inicia uvicorn con `src.infrastructure.fastapi.app_fastapi:app` en el puerto 5005.
  - Modo espejo (eco): `python run.py mode=ESPEJO` o `--espejo` para probar integración Rasa-like sin dependencias externas.
  - Entrenar Rasa con rutas internas: `python run.py --train` (usa `src/infrastructure/rasa` y escribe modelos en `src/infrastructure/rasa/models`). Nota: `RASA_HOME` se establece para aislar archivos `.rasa`.
  - Ejecutar Rasa con el modelo más reciente: `python run.py --rasa` o `python run.py mode=RASA` (busca el .tar.gz más reciente en `src/infrastructure/rasa/models`).

5) Patrones y convenciones de código
  - Dependencias inyectadas manualmente: infraestructura crea instancias (p.ej. `GeminiService`) y las pasa a puertas/gateways y casos de uso. Prefiere modificar composición en `app_fastapi.create_app` para nuevas pruebas.
  - Entidades ligeras y adaptadores: `src/entities/*` define contratos (p.ej. `GeminiResponder`, `SystemInstructions`) y los gateways respetan esas firmas.
  - Config centralizada: `src/shared/config.py` usa `python-dotenv`; los agentes deben leer config mediante `get_config()` en lugar de acceder directamente a `os.environ`.
  - Logging: usa `src/shared/logger.py` (con get_logger). Emplear niveles DEBUG/INFO para diagnosticar.

6) Integraciones y riesgos a documentar
  - Google Generative AI (`google.generativeai`) — requiere key; fallos al inicializar se elevan desde `GeminiService.__init__`.
  - Rasa CLI y runtime — las rutas de Rasa están en `src/infrastructure/rasa`. `run.py` invoca `rasa train` y `rasa run` como subprocesos; validar que `rasa` esté en PATH del entorno usado.
  - Repositorio de instrucciones JSON: `src/infrastructure/google_generative_ai/system_instructions.json` puede estar presente — `SYSTEM_INSTRUCTIONS_PATH` apunta a él.

7) Reglas prácticas para el agente (qué hacer/evitar)
  - Haz cambios en la composición de dependencias en `create_app` para evitar tocar lógica de negocio en `GeminiService` o `GeminiGateway` salvo que sea un bug localizado.
  - Para probar la parte de Gemini sin clave real, usar `mode=ESPEJO` o mockear `GeminiService.get_response` en tests/unit.
  - No elimines la configuración de `RASA_HOME` en `run.py`; está diseñada para aislar el workspace de Rasa.
  - Cuando modifiques prompts/instrucciones: documenta la clave JSON y su esquema (se busca `instructions` por defecto en `GeminiService.load_system_instructions_from_json`).

8) Ejemplos concretos de edición y pruebas
  - Añadir logging adicional antes/después de la llamada a Gemini: editar `src/infrastructure/fastapi/app_fastapi.py` en ruta donde se llama `gemini.get_response(...)`.
  - Para soportar otro modelo o proveedor: implementar un nuevo servicio que implemente `GeminiResponder.get_response` y registrar la instancia en `create_app`.
  - Para tests rápidos de endpoint webhook (modo GOOGLE_GEMINI):
    - Levanta la app: `python run.py mode=GOOGLE_GEMINI` (o con `APP_MODE=GOOGLE_GEMINI python -m uvicorn src.infrastructure.fastapi.app_fastapi:app --reload --port 5005`)
    - POST a `http://localhost:5005/webhooks/rest/webhook` con JSON `{ "sender": "u1", "message": "hola" }`.

9) Archivos relevantes (referencias rápidas)
  - `run.py` — orquestador y comandos de entrenamiento/ejecución.
  - `src/infrastructure/fastapi/app_fastapi.py` — composición de la app FastAPI y webhook.
  - `src/infrastructure/google_generative_ai/gemini_service.py` — cliente de Gemini.
  - `src/interface_adapter/gateways/gemini_gateway.py` — adaptador entre servicio y entidades.
  - `src/use_cases/load_system_instructions.py` y `src/infrastructure/repositories/json_instructions_repository.py` — carga de instrucciones.
  - `src/shared/config.py`, `src/shared/logger.py` — configuración y logging.

10) Preguntas útiles para el mantenedor (si necesitas clarificar)
  - ¿Hay tests unitarios que debamos conocer o un runner preferido? (no se encontraron tests en la raíz).
  - ¿Dónde suelen almacenar el JSON de instrucciones en producción (S3, ruta local)?

Si quieres, hago una segunda pasada: puedo acortar o ampliar ejemplos, añadir snippets de tests unitarios para `GeminiGateway` y `app_fastapi` o integrar CI/CD hints.
