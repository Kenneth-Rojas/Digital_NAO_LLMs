# Sprint 3: Chatbot con Gradio

## Descripción General

Este sprint implementa **CueBot**, un chatbot inteligente basado en análisis de documentos PDF. El proyecto está compuesto por dos componentes principales:

1. **API REST (`api_cuebot_llm.py`)**: Una API construida con FastAPI que procesa solicitudes de análisis de texto. Normaliza entradas de diferentes formatos, integra el modelo LLM de Google Gemini para generar respuestas inteligentes, y proporciona un fallback a un generador local basado en palabras clave cuando el API externo no está disponible.

2. **Interfaz Gradio (`cuebot_llm.py`)**: Una interfaz gráfica web que permite a los usuarios subir archivos PDF, extraer su contenido automáticamente y hacer preguntas sobre el texto. La interfaz se comunica con la API REST y presenta las respuestas con un efecto de escritura progresiva para mejorar la experiencia del usuario.

El flujo es: usuario sube PDF → se extrae el texto → usuario hace una pregunta → API analiza el PDF + pregunta con Gemini → respuesta se muestra en la interfaz.


### Requisitos Previos

- Python 3.8 o superior, no mayor a 3.11
- pip (gestor de paquetes de Python)
- Una clave API válida de Google GenAI (obtenerla en [Google AI Studio](https://aistudio.google.com))

---

## 📋 Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/Kenneth-Rojas/Digital_NAO_LLMs.git
cd Digital_NAO_LLMs/Sprint3
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
- `fastapi`: Framework web ligero para construir APIs en Python.
- `uvicorn`: Servidor ASGI rápido para ejecutar la aplicación FastAPI.
- `gradio`: Framework para crear interfaces de usuario web para aplicaciones Python, utilizado para la interfaz del chatbot CueBot.
- `requests`: Librería HTTP para realizar solicitudes POST/GET a la API desde la interfaz Gradio.

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
uvicorn api_cuebot_llm:app --reload
```

La API quedará disponible por defecto en `http://127.0.0.1:8000`.

## Ejecutar el ChatBot

```bash
python cuebot_llm.py
```
El bot quedará disponible por defecto en `http://127.0.0.1:7860` .
---


## Notas importantes

- **Soporte de archivos**: `.pdf`.
- **Variables de entorno**: Nunca subas tu clave a repositorios públicos. Usa `.env` local.
- **Dependencias**: Si falta alguna librería, el servidor arrojará un error indicando qué instalar.

---

## Autor

Kenneth Rojas - [GitHub](https://github.com/Kenneth-Rojas)

---

**Última actualización**: Enero 2026
