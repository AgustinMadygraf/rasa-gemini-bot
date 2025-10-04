# Rasa Gemini Bot

Este proyecto integra un bot conversacional compatible con Rasa y Google Gemini, con soporte para transcripción de audio local (Vosk/Google) y un modo espejo para pruebas.

## Requisitos

- Python 3.8 o superior
- [pip](https://pip.pypa.io/en/stable/)
- Modelos de Vosk (para transcripción offline)

## Instalación

1. **Clona el repositorio**  
   ```sh
   git clone https://github.com/AgustinMadyraf/rasa-gemini-bot.git
   cd rasa-gemini-bot
   ```

2. **Crea y activa un entorno virtual**  
   ```sh
   python -m venv venv
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias**  
   ```sh
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configura el archivo `.env`**  
   Copia el archivo de ejemplo y renómbralo a `.env`.  
   Asegúrate de completar las variables necesarias.
   ```sh
   copy .env.example .env
   ```

5. **Obtén tus credenciales de Google Gemini:**  
   Regístrate en [Google AI Studio](https://aistudio.google.com/app/apikey) y genera una API Key.  
   Luego, copia tu clave en la variable `GOOGLE_GEMINI_API_KEY` dentro del archivo `.env`.

6. **Configura las instrucciones del sistema:**  
   Copia el archivo de ejemplo de instrucciones del sistema (`system_instructions.json`) en la ruta indicada por `SYSTEM_INSTRUCTIONS_PATH` en tu `.env`.  
   Personaliza su contenido según las necesidades de tu bot.

7. **Descarga un modelo de Vosk**  
   Por ejemplo, para español:
   ```powershell
   Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip" -OutFile "vosk-model-small-es-0.42.zip"
   Expand-Archive vosk-model-small-es-0.42.zip -DestinationPath model
   ```
   Asegúrate de que el contenido del modelo quede directamente dentro de la carpeta `model/`.

## Uso

### Ejecutar el bot

- **Modo Gemini:**
  ```sh
  python run.py --gemini
  ```

- **Modo Espejo (eco de mensajes):**
  ```sh
  python run.py --espejo
  ```

- **Modo Rasa (requiere Rasa instalado):**
  ```sh
  python run.py --rasa
  ```

Si no se proporciona un argumento, el modo se tomará de la variable `MODE` definida en el archivo `.env`.

### Transcribir un archivo de audio (experimental)

```sh
python run_transcriber.py
```
Sigue las instrucciones para ingresar la ruta del archivo de audio.

## Estructura del proyecto

```
rasa-gemini-bot/
│
├─ run.py                  # Punto de entrada principal
├─ run_transcriber.py      # Transcriptor de audio por CLI
├─ requirements.txt
├─ model/                  # Modelo Vosk descargado
│
├─ src/
│   ├─ infrastructure/
│   │   ├─ fastapi/
│   │   │   └─ app_fastapi.py
│   │   └─ audio/
│   │       └─ local_audio_transcriber.py
│   ├─ use_cases/
│   ├─ entities/
│   └─ shared/
│
└─ ...
```

## Notas

- Para usar la transcripción offline, asegúrate de que la carpeta `model/` contenga el modelo Vosk descomprimido correctamente (sin subcarpetas intermedias).
- Si el modelo no está disponible, se utilizará Google Speech Recognition (requiere conexión a Internet).
- Configura tus variables en el archivo `.env` según sea necesario.

---

¿Tienes dudas o problemas? Abre un issue o consulta la documentación de las dependencias utilizadas.