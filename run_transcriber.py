"""
Path: run_transcriber.py
"""

from src.infrastructure.audio.local_audio_transcriber import LocalAudioTranscriber

if __name__ == "__main__":
    app = LocalAudioTranscriber()
    audio_file_path = input("Ingrese la ruta del archivo de audio: ")
    try:
        transcription = app.transcribe(audio_file_path)
        print(f"Transcripción: {transcription.text}")
    except FileNotFoundError as e:
        print(f"No se encontró el archivo: {e}")
        print("Intentando fallback: transcripción vacía.")
        print("Transcripción: ")
    except PermissionError as e:
        print(f"No se tienen permisos para acceder al archivo: {e}")
        print("Intentando fallback: transcripción vacía.")
        print("Transcripción: ")
    except OSError as e:
        print(f"Ocurrió un error de sistema durante la transcripción: {e}")
        print("Intentando fallback: transcripción vacía.")
        print("Transcripción: ")
