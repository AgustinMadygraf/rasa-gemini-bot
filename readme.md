# Rasa Gemini Bot

## 📢 Descripción
Rasa Gemini Bot es un motor conversacional flexible que combina la estructura de Rasa con el poder generativo de Google Gemini. Su arquitectura limpia y modular permite operar en distintos modos y facilita la integración con sistemas externos como [Messenger Bridge](https://github.com/AgustinMadygraf/messenger-bridge), llevando experiencias conversacionales inteligentes a WhatsApp, Telegram y más.

## ✨ Características principales
- 🔄 **Multi-modalidad**: Elige entre respuestas basadas en intenciones (Rasa), generación avanzada (Gemini) o modo espejo para pruebas.
- 🧠 **Arquitectura limpia**: Separación clara entre entidades, lógica de negocio, adaptadores y servicios externos.
- 🌐 **API REST y FastAPI**: Endpoints compatibles con webhooks de Rasa y fácil integración con Messenger Bridge.
- 💾 **Gestión de contexto**: Mantiene el historial y contexto de la conversación para respuestas más precisas.
- 🔌 **Extensible y adaptable**: Listo para integrarse con nuevos canales o motores conversacionales.

## 🚀 Modos de operación

- **RASA**: Bot tradicional basado en intenciones y respuestas predefinidas.
- **GOOGLE_GEMINI**: Generación dinámica de respuestas mediante IA de Google Gemini.
- **ESPEJO**: Devuelve el mensaje recibido, útil para pruebas y debugging.

## 🏗️ Estructura del proyecto

```
.
├── actions/               # Acciones personalizadas de Rasa
├── data/                  # Datos de entrenamiento (NLU, reglas, historias)
├── docs/                  # Documentación
├── model/                 # Modelos entrenados de Rasa
├── src/                   # Código principal
│   ├── entities/          # Entidades de negocio
│   ├── infrastructure/    # Servicios externos
│   ├── interface_adapter/ # Adaptadores y controladores
│   ├── shared/            # Utilidades comunes
│   └── use_cases/         # Lógica de negocio
└── tests/                 # Pruebas automatizadas
```

## 🔧 Inicio rápido

1. Crea y activa un entorno virtual.
2. Instala dependencias: `pip install -r requirements.txt`
3. Copia `.env.example` a `.env` y configura tus variables.
4. Ejecuta el bot: `python run.py` o `run.bat` (Windows).

Consulta la [guía de instalación](docs/installation.md) para más detalles.

## 🔌 Integración con Messenger Bridge

Rasa Gemini Bot está diseñado para funcionar como motor conversacional detrás de Messenger Bridge, permitiendo interacción multicanal (WhatsApp, Telegram, etc.) con una lógica centralizada.

### Diagrama de flujo
```
Usuario (WhatsApp/Telegram) → Messenger Bridge → Rasa Gemini Bot → Messenger Bridge → Usuario
```

## 🌐 API

- Endpoint: `/webhooks/rest/webhook`
- Método: POST
- Ejemplo de cuerpo:
  ```json
  {
    "sender": "user_id",
    "message": "mensaje del usuario"
  }
  ```

Más detalles en la [Documentación de API](docs/API_document.md).

## ⚙️ Configuración

Variables principales en `.env`:

- `GOOGLE_GEMINI_API_KEY`
- `GOOGLE_GEMINI_MODEL`
- `LOG_LEVEL`
- `SYSTEM_INSTRUCTIONS_PATH`
- `MODE`

## 🗺️ Roadmap

Próximas mejoras y objetivos:

- [ ] **Fallback inteligente**: Si Rasa no entiende, delegar la respuesta a Google Gemini.
- [ ] **Chatbot asistente de instalación**: Instrucciones de sistema y entrenamiento para ayudar a instalar y configurar Rasa.
- [ ] **Optimización de archivos de entrenamiento**: Ajustar `nlu.yml`, `domain.yml`, etc. para mejorar la experiencia de onboarding y soporte.

¿Tienes ideas o sugerencias? ¡Tu aporte es bienvenido!

## 🤝 Cómo contribuir

Consulta la [guía de contribución](docs/CONTRIBUTING.md) para participar en el desarrollo.

## 📄 Licencia

Distribuido bajo la licencia MIT. Más información en [LICENSE](LICENSE).

---

<p align="center">
  Desarrollado con ❤️ por la comunidad
</p>