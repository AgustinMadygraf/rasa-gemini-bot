# Rasa Gemini Bot

> Motor conversacional flexible que combina la orquestación de **Rasa 3.6** con generación de texto vía **Google Gemini**, listo para integrarse con canales como WhatsApp y Telegram mediante [Messenger Bridge](https://github.com/AgustinMadygraf/messenger-bridge).

## ✨ Funcionalidades

* 🔀 **Modos de operación**:

  * **RASA** (intenciones y reglas/historias)
  * **GOOGLE_GEMINI** (respuestas generativas)
  * **ESPEJO** (eco para pruebas)
* 🧱 **Arquitectura limpia** (capas de entidades, casos de uso, infraestructura y adaptadores).
* 🌐 **API REST** (FastAPI + webhook de Rasa).
* 💬 **Contexto y estado** de conversación.
* 🔌 **Extensible**: acciones personalizadas, nuevos canales, servicios externos.

## 🗂️ Estructura del proyecto

```
.
├── src/
│   ├── entities/
│   ├── use_cases/
│   ├── interface_adapter/
│   ├── shared/
│   └── infrastructure/
│       ├── rasa/
│       │   ├── actions/        # Acciones personalizadas de Rasa (Python)
│       │   ├── data/           # nlu.yml, rules.yml, stories.yml
│       │   ├── domain.yml      # ¡OJO! No está en el root
│       │   └── config.yml      # ¡OJO! No está en el root (language: es)
│       ├── fastapi/
│       └── google_generativeai/
├── docs/
└── tests/
```

## ✅ Requisitos

* **Python 3.10.x** (recomendado 3.10.11)
* **Rasa 3.6.x** / **Rasa SDK 3.6.x**
* pip, venv
* (Opcional) Git

## 🚀 Inicio rápido

### 1) Clonar y preparar entorno

```bash
git clone https://github.com/AgustinMadygraf/rasa-gemini-bot
cd rasa-gemini-bot

# venv (Windows)
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate

# venv (macOS/Linux)
python -m venv venv
source venv/bin/activate
```

### 2) Instalar dependencias

```bash
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
# Si Rasa no está en requirements.txt:
pip install "rasa==3.6.*" "rasa-sdk==3.6.*"
```

### 3) Variables de entorno (.env)

```bash
cp .env.example .env
```

Configura, por ejemplo:

```
GOOGLE_GEMINI_API_KEY=tu_api_key
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash
LOG_LEVEL=INFO
SYSTEM_INSTRUCTIONS_PATH=src/infrastructure/google_generativeai/system_instructions.json
MODE=GOOGLE_GEMINI   # o RASA / ESPEJO
```

### 4) Entrenar modelo Rasa (rutas reales)

> El `domain.yml`, `config.yml` y los datos están en `src/infrastructure/rasa/`.

```powershell
# Validar datos
rasa data validate --domain .\src\infrastructure\rasa\domain.yml --config .\src\infrastructure\rasa\config.yml --data .\src\infrastructure\rasa\data

# Entrenar (deja el modelo en .\models)
rasa train --domain .\src\infrastructure\rasa\domain.yml --config .\src\infrastructure\rasa\config.yml --data .\src\infrastructure\rasa\data --out .\models
```

### 5) Ejecutar

**Servidor de acciones** (si usas acciones en `src/infrastructure/rasa/actions/`):

```bash
# Asegura PYTHONPATH para que Python pueda importar desde ./src
# Windows (PowerShell):
$env:PYTHONPATH = (Resolve-Path .\src).Path
rasa run actions --actions src.infrastructure.rasa.actions

# macOS/Linux:
export PYTHONPATH="$(pwd)/src"
rasa run actions --actions src.infrastructure.rasa.actions
```

**Bot (shell o API)**:

```powershell
# Elegir el modelo más reciente
$Model = (Get-ChildItem .\models\*.tar.gz | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName

# Shell interactivo (sin --domain)
rasa shell --debug -m $Model

# Servir API REST
rasa run --enable-api --cors "*" --debug -m $Model
```

**Endpoints REST** (Rasa):

```
POST http://localhost:5005/webhooks/rest/webhook
{
  "sender": "usuario123",
  "message": "Hola"
}
```

### 6) Ejecutar con `run.py` (modos)

```bash
python run.py              # usa MODE de .env
python run.py --rasa
python run.py --gemini
python run.py --espejo
```

## 🔌 Integración con Messenger Bridge

El bot puede actuar como motor detrás de Messenger Bridge (WhatsApp/Telegram).
Flujo:

```
Usuario → Messenger Bridge → Rasa Gemini Bot → Messenger Bridge → Usuario
```

## ⚙️ Notas importantes de configuración (Rasa 3.6)

* `src/infrastructure/rasa/config.yml` debe tener **`language: es`** (no `ess`).
* **Forms en Rasa 3** se gestionan con **RulePolicy** (no FormPolicy). Activa/desactiva con `rules` y `active_loop`.
* **Usa `--domain` y `--config` solo en `validate/train/test`**.
  En `shell/run`, **no** pases `--domain`; usa `-m <ruta_al_modelo.tar.gz>`.

## 🧪 Scripts útiles

**`dev-run.ps1`** (opcional, colócalo en el root):

```powershell
param(
  [string]$Domain = ".\src\infrastructure\rasa\domain.yml",
  [string]$Config = ".\src\infrastructure\rasa\config.yml",
  [string]$Data   = ".\src\infrastructure\rasa\data"
)

Write-Host "== Validación ==" -ForegroundColor Cyan
rasa data validate --domain $Domain --config $Config --data $Data

Write-Host "== Entrenando ==" -ForegroundColor Cyan
rasa train --domain $Domain --config $Config --data $Data --out .\models

Write-Host "== Modelo ==" -ForegroundColor Cyan
$Model = (Get-ChildItem .\models\*.tar.gz | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
if (-not $Model) { throw "No se encontró modelo en .\models" }

Write-Host "== Shell ==" -ForegroundColor Cyan
rasa shell --debug -m $Model
```

## 🛠️ Solución de problemas

* **`config.yml` no encontrado** → pásalo con `--config .\src\infrastructure\rasa\config.yml`.
* **`domain.yml` no encontrado** → pásalo con `--domain .\src\infrastructure\rasa\domain.yml`.
* **`No training data given`** → usa `--data .\src\infrastructure\rasa\data` o coloca tus `nlu.yml / stories.yml / rules.yml` allí.
* **Warnings “intent/utterance no usado”** → alinea `domain.yml` con tus `nlu/stories/rules`.
* **`InvalidRule: Contradicting rules or stories found`**

  * En historias no fuerces una acción si existe una **regla** que predice otra para el mismo contexto.
  * Para **forms**: activa con `rules` (`active_loop: mi_form`) y evita historias que predigan acciones contradictorias en esos turnos.
  * Revisa que el flujo “asistencia técnica” no pida **`instalar_rasa_form`** en historias si la **regla** espera **`utter_asistencia_tecnica`** (unifica: o regla o historia, no ambas con outcomes distintos).
* **Multilínea en PowerShell** → el *backtick* debe ser el **último** carácter de línea. Si falla, usa **one-liners**.
* **Avisos SQLAlchemy 2.0** → fija `sqlalchemy<2.0` en `requirements.txt` si molestan.

## 📄 Documentación adicional

* Guía detallada de instalación: `docs/installation.md`
* API: `docs/API_document.md`

## 🤝 Contribución

Consulta `docs/CONTRIBUTING.md` y abre PRs/Issues con mejoras o bugs.

## 📜 Licencia

MIT — ver `LICENSE`.

---

<p align="center">
  Desarrollado con ❤️ por la comunidad
</p>