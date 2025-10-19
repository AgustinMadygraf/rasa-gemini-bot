# Guía de Instalación

Esta guía te lleva desde cero hasta tener **Rasa Gemini Bot** funcionando en **modo RASA**, **GOOGLE_GEMINI** o **ESPEJO**, con especial atención a las rutas reales del proyecto.

---

## 1) Requisitos

* **Python 3.10.x** (recomendado: 3.10.11)
* **pip**, **venv**
* **Rasa 3.6.x**, **Rasa SDK 3.6.x**
* (Opcional) Git

Verifica versiones:

```bash
python --version
rasa --version
```

---

## 2) Clonar y crear entorno

```bash
git clone https://github.com/AgustinMadygraf/rasa-gemini-bot
cd rasa-gemini-bot
```

### Windows (PowerShell)

```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

---

## 3) Instalar dependencias

```bash
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
# Si Rasa/SDK no están en requirements:
pip install "rasa==3.6.*" "rasa-sdk==3.6.*"
```

---

## 4) Variables de entorno (.env)

Copia el ejemplo y ajusta valores:

```bash
cp .env.example .env
```

Variables típicas:

```
GOOGLE_GEMINI_API_KEY=tu_api_key
GOOGLE_GEMINI_MODEL=models/gemini-2.5-flash
LOG_LEVEL=INFO
SYSTEM_INSTRUCTIONS_PATH=src/infrastructure/google_generativeai/system_instructions.json
MODE=GOOGLE_GEMINI   # o RASA / ESPEJO
```

(Para modo **Gemini**: copia también el JSON de instrucciones y edítalo a tu gusto).

```bash
cp src/infrastructure/google_generativeai/system_instructions.json.example \
   src/infrastructure/google_generativeai/system_instructions.json
```

---

## 5) Rutas importantes (¡ojo!)

En este proyecto **Rasa no está en el root**:

* **Domain**: `src/infrastructure/rasa/domain.yml`
* **Config**: `src/infrastructure/rasa/config.yml`  (asegúrate: `language: es`)
* **Data**:   `src/infrastructure/rasa/data/`  (contiene `nlu.yml`, `rules.yml`, `stories.yml`)

> Por eso, en **validate/train/test** debes pasar **`--domain`** y **`--config`** con esas rutas.
> En **shell/run**, **no** pases `--domain`; usa **`-m`** con el modelo entrenado.

---

## 6) Entrenar modelo Rasa

### Validar datos

```powershell
rasa data validate `
  --domain .\src\infrastructure\rasa\domain.yml `
  --config .\src\infrastructure\rasa\config.yml `
  --data .\src\infrastructure\rasa\data
```

*(En PowerShell, si falla por multilínea, usa una sola línea.)*

### Entrenar

```powershell
rasa train `
  --domain .\src\infrastructure\rasa\domain.yml `
  --config .\src\infrastructure\rasa\config.yml `
  --data .\src\infrastructure\rasa\data `
  --out .\models
```

---

## 7) Ejecutar

### 7.1 Servidor de **acciones** (si usas `src/infrastructure/rasa/actions/`)

Asegura `PYTHONPATH` para importar desde `./src`:

**Windows (PowerShell):**

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
rasa run actions --actions src.infrastructure.rasa.actions
```

**macOS / Linux:**

```bash
export PYTHONPATH="$(pwd)/src"
rasa run actions --actions src.infrastructure.rasa.actions
```

### 7.2 Bot (Shell o API)

Selecciona el modelo más reciente:

```powershell
$Model = (Get-ChildItem .\models\*.tar.gz | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
```

**Shell interactivo:**

```powershell
rasa shell --debug -m $Model
```

**API REST de Rasa:**

```powershell
rasa run --enable-api --cors "*" --debug -m $Model
```

**Probar REST:**

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender":"usuario123","message":"Hola"}'
```

---

## 8) Ejecutar con `run.py` (modos)

```bash
python run.py              # usa MODE del .env
python run.py --rasa
python run.py --gemini
python run.py --espejo
```

---

## 9) Tareas comunes

* **Re-entrenar** tras cambios en `nlu.yml`, `rules.yml`, `stories.yml` o `domain.yml`.
* **Validación** rápida:

  ```bash
  rasa data validate --domain src/infrastructure/rasa/domain.yml --config src/infrastructure/rasa/config.yml --data src/infrastructure/rasa/data
  ```
* **Tests** (si tienes):

  ```bash
  rasa test -m models/<tu_modelo>.tar.gz --domain src/infrastructure/rasa/domain.yml --stories src/infrastructure/rasa/data/stories.yml --nlu src/infrastructure/rasa/data/nlu.yml
  ```
* **Limpiar modelos antiguos:**

  ```powershell
  Remove-Item .\models\* -Force
  ```

---

## 10) Solución de problemas

### `config.yml` / `domain.yml` no encontrados

* Asegúrate de pasar las rutas reales:

  ```
  --config .\src\infrastructure\rasa\config.yml
  --domain .\src\infrastructure\rasa\domain.yml
  --data   .\src\infrastructure\rasa\data
  ```

### “No training data given”

* `--data` debe apuntar a la carpeta que contiene `nlu.yml`, `rules.yml`, `stories.yml`. En este repo: `src/infrastructure/rasa/data`.

### `language: ess`

* Debe ser `language: es` en `src/infrastructure/rasa/config.yml`.

### `InvalidRule: Contradicting rules or stories found`

Ejemplo real:

```
the prediction of the action 'instalar_rasa_form' in story 'asistencia tecnica despues de saludo'
is contradicting with rule(s) 'Activar formulario instalar_rasa_form' which predicted action 'utter_asistencia_tecnica'
```

**Cómo resolver:**

* Evita que **historias** predigan una acción distinta a la que una **regla** ya fija para el mismo contexto.
* Para **forms** en Rasa 3:

  * Activa con **rule** usando `active_loop: <mi_form>`.
  * No fuerces en historias una acción diferente en el turno de activación.
  * Mantén coherentes los pasos de `requested_slot` y desactivación.
* Alternativas:

  * Quita la historia contradictoria o ajusta su acción al mismo outcome que la regla.
  * Si una historia debe gobernar ese flujo, elimina la regla específica.

### Intents/utterances no usados o desalineados

* Si ves *“intent X not used in any story or rule”* o *utterances no usadas*, ajusta:

  * Agrega el intent a historias/reglas o elimínalo si no se usa.
  * Usa las `utter_...` en stories/rules o elimínalas del `domain.yml`.
* *“message labeled with intent 'informar_proyecto' not in domain”* → añade el intent al `domain.yml`.

### Warnings SQLAlchemy 2.0 (ruido)

* Ancla versión en `requirements.txt`:

  ```
  SQLAlchemy<2.0
  ```

### Multilínea en PowerShell

* El backtick **`** debe ser el **último** carácter de la línea (sin espacios después). Si falla, usa una sola línea.

---

## 11) Scripts opcionales

### `dev-run.ps1` (Windows)

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

$Model = (Get-ChildItem .\models\*.tar.gz | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
if (-not $Model) { throw "No se encontró modelo en .\models" }

Write-Host "== Shell ==" -ForegroundColor Cyan
rasa shell --debug -m $Model
```

### `dev-run.sh` (macOS/Linux)

```bash
#!/usr/bin/env bash
set -euo pipefail

DOMAIN=src/infrastructure/rasa/domain.yml
CONFIG=src/infrastructure/rasa/config.yml
DATA=src/infrastructure/rasa/data

rasa data validate --domain "$DOMAIN" --config "$CONFIG" --data "$DATA"
rasa train --domain "$DOMAIN" --config "$CONFIG" --data "$DATA" --out models

MODEL=$(ls -t models/*.tar.gz | head -n1)
rasa shell --debug -m "$MODEL"
```

---

## 12) Verificación rápida

```bash
# Comprobar rutas
test -f src/infrastructure/rasa/domain.yml
test -f src/infrastructure/rasa/config.yml
test -f src/infrastructure/rasa/data/nlu.yml

# Ver versión Rasa
rasa --version
```

