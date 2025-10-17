# Guía de Instalación

Esta guía te ayudará a instalar y ejecutar **Rasa Gemini Bot** paso a paso.

## Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

## 1. Clona o descarga el repositorio

```bash
git clone https://github.com/AgustinMadygraf/rasa-gemini-bot
cd rasa-gemini-bot
```

O descarga y descomprime el archivo ZIP desde el repositorio.

## 2. verifica la version correcta y luego crea un entorno virtual

### Windows

```bash
python --version # debe ser 3.10
py --list
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\activate
```

https://www.python.org/downloads/release/python-31011/

### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Instala las dependencias

```bash
python.exe -m pip install --upgrade pip
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
python -m pip install rasa
```

Esto instalará todos los paquetes necesarios, incluyendo Rasa, FastAPI, el SDK de Google Gemini y otras dependencias.

## 4. Configura las variables de entorno

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Edita el archivo `.env` y agrega tu configuración:

```
GOOGLE_GEMINI_API_KEY=tu_api_key_de_gemini
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash
LOG_LEVEL=INFO
SYSTEM_INSTRUCTIONS_PATH=src/infrastructure/google_generative_ai/system_instructions.json
MODE=GOOGLE_GEMINI
```

## 5. Configura las instrucciones del sistema (modo Gemini)

1. Copia el archivo de ejemplo:

```bash
cp src/infrastructure/google_generative_ai/system_instructions.json.example src/infrastructure/google_generative_ai/system_instructions.json
```

2. Edita el archivo JSON para personalizar las instrucciones que recibe el modelo Gemini.

## 6. Entrena el modelo de Rasa (modo RASA)

Si vas a usar el modo RASA, primero entrena el modelo:

```bash
rasa train
```

## 7. Ejecuta el bot

### Usando el script principal

```bash
python run.py
```

### Especificando el modo

```bash
python run.py --rasa      # Modo Rasa
python run.py --gemini    # Modo Gemini
python run.py --espejo    # Modo Espejo
```

### En Windows

También puedes usar el archivo por lotes:

```bash
run.bat
```

## 8. Prueba el bot

Una vez iniciado, puedes interactuar de las siguientes formas:

1. **Rasa Shell** (solo modo RASA):
   ```bash
   rasa shell
   ```

2. **Solicitudes HTTP** al endpoint REST:
   ```bash
   curl -X POST http://localhost:5005/webhooks/rest/webhook \
     -H "Content-Type: application/json" \
     -d '{"sender": "usuario123", "message": "Hola"}'
   ```

## Solución de problemas

### Problemas comunes

1. **API Key faltante**: Verifica que tu clave de Gemini esté correctamente en `.env`.
2. **Modelo no encontrado**: Si usas modo RASA y aparece "model not found", asegúrate de haber entrenado el modelo con `rasa train`.
3. **Errores de importación**: Revisa que todas las dependencias estén instaladas con `pip install -r requirements.txt`.
4. **Conflicto de puertos**: Si el puerto 5005 está ocupado, modifica el puerto en `run.py` o detén el servicio en conflicto.

### ¿Necesitas ayuda?

Si tienes problemas no cubiertos aquí, revisa la sección de issues del repositorio o abre uno nuevo.

---