# Sprint 2: API REST

## Descripción General

Este sprint contiene una API REST construida con FastAPI que permite procesar texto o archivos y obtener respuestas generadas por un modelo LLM (Gemini) a través del SDK de `google-genai`.

El punto de entrada principal es el archivo [fastapi_llm.py](fastapi_llm.py) y la aplicación también sirve una interfaz estática en [static/index.html](static/index.html) si existe.

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Una clave API válida de Google GenAI (obtenerla en [Google AI Studio](https://aistudio.google.com))

---

## 📋 Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/Kenneth-Rojas/Digital_NAO_LLMs.git
cd Digital_NAO_LLMs/Sprint2
```

### 2. Crear un entorno virtual

#### En **Linux/macOS**:

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
```

#### En **Windows** (PowerShell):

```powershell
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\Activate.ps1
```

#### En **Windows** (Command Prompt):

```cmd
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
venv\Scripts\activate.bat
```

### 3. Instalar las dependencias

Una vez activado el entorno virtual, instala los paquetes requeridos:

```bash
pip install -r requirements.txt
```
**Dependencias incluidas:**
- `google-genai`: SDK de Google para acceder a los modelos GenAI
- `python-dotenv`: Para cargar variables de entorno desde archivos `.env`
- `PyPDF2`: Para leer y procesar archivos PDF
- `fastapi`:
- `uvicorn`:
 - `fastapi`: Framework web ligero para construir APIs en Python.
 - `uvicorn`: Servidor ASGI rápido para ejecutar la aplicación FastAPI.
---

## Configurar la clave API

Crea un archivo `.env` en la raíz de `Sprint2` con la variable `GENAI_API_KEY`:

```bash
echo "GENAI_API_KEY=tu_clave_api_aqui" > .env
```
---

## Ejecutar la API

Iniciar la aplicación con `uvicorn`:

```bash
uvicorn fastapi_llm:app --reload
```

La API quedará disponible por defecto en `http://127.0.0.1:8000`.

---


## Notas importantes

- **Soporte de archivos**: `.txt`, `.md` y `.pdf`.
- **Variables de entorno**: Nunca subas tu clave a repositorios públicos. Usa `.env` local.
- **Dependencias**: Si falta alguna librería, el servidor arrojará un error indicando qué instalar.

---

## Autor

Kenneth Rojas - [GitHub](https://github.com/Kenneth-Rojas)

---

**Última actualización**: Diciembre 2025
