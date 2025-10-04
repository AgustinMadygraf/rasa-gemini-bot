# Rasa Gemini Bot

Este proyecto integra un bot conversacional compatible con Rasa y Google Gemini, con soporte para transcripción de audio local (Vosk/Google) y un modo espejo para pruebas.

## Requisitos

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- [ffmpeg](https://ffmpeg.org/) (para pydub)
- Modelos de Vosk (para transcripción offline)

## Instalación

1. **Clona el repositorio**  
   ```sh
   git clone https://github.com/tu_usuario/rasa-gemini-bot.git
   cd rasa-gemini-bot
   ```

2. **Crea y activa un entorno virtual**  
   ```sh
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instala las dependencias**  
   ```sh
   pip install -r requirements.txt
   ```

4. **Instala ffmpeg**  
   Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html) y agrega el ejecutable a tu variable de entorno `PATH`.

5. **Descarga un modelo de Vosk**  
   Ejemplo para español:
   ```powershell
   Invoke-WebRequest -Uri "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip" -OutFile "model/vosk-model-small-es-0.42.zip"
   Expand-Archive vosk-model-small-es-0.42.zip -DestinationPath model
   ```

## Uso

### Ejecutar el bot

- **Modo Gemini (por defecto o con .env):**
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

### Transcribir un archivo de audio

```sh
python run_transcriber.py
```
Sigue las instrucciones para ingresar la ruta del archivo de audio.

## Estructura del proyecto

```
rasa-gemini-bot/
│
├─ run.py                  # Entry point principal
├─ run_transcriber.py      # Transcriptor de audio CLI
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

- Para usar la transcripción offline, asegúrate de que la carpeta `model/` contenga el modelo Vosk descomprimido.
- Si el modelo no está disponible, se usará Google Speech Recognition (requiere Internet).
- Configura tus variables en `.env` según sea necesario.

---

¿Dudas o problemas? Abre un issue o consulta la documentación de cada dependencia.