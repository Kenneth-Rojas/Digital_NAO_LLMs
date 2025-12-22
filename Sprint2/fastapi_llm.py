import os
import sys
import textwrap
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

try:
    from google import genai
except Exception:
    genai = None

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    import PyPDF2
except Exception:
    PyPDF2 = None

from fastapi.middleware.cors import CORSMiddleware

# Inicializar FastAPI
app = FastAPI(
    title="LLM API",
    description="API REST para interactuar con Gemini"
    )

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar archivos estáticos
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Modelos de datos
class TextRequest(BaseModel):
    """Modelo para peticiones con texto directo."""
    text: str
    instruction: str = "Realiza un resumen a manera de 5 viñetas del contenido de la siguiente información."
    model: str = "gemini-2.5-flash"


class FileRequest(BaseModel):
    """Modelo para respuestas de archivo."""
    filename: str
    instruction: str
    model: str = "gemini-2.5-flash"


# Funciones auxiliares
def initialize_genai():
    """Inicializa el cliente de Gemini con la API key."""
    if genai is None:
        raise RuntimeError(
            "La librería 'google.genai' no está instalada. Instálala con: "
            "pip install google-genai"
        )

    if load_dotenv is None:
        raise RuntimeError(
            "La librería 'python-dotenv' no está instalada. Instálala con: "
            "pip install python-dotenv"
        )

    load_dotenv()
    api_key = os.environ.get("GENAI_API_KEY")

    try:
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            client = genai.Client()
    except TypeError:
        client = genai.Client()

    return client


def build_messages(content: str, instruction: str, language: str = "es"):
    """Construye los mensajes para el modelo LLM."""
    system = {
        "role": "system",
        "content": (
            f"Eres un asistente experto que procesa información y textos. "
            "Responde con precisión y claridad, manteniendo un tono profesional."
        ),
    }

    user = {
        "role": "user",
        "content": textwrap.dedent(
            f"""
        {instruction}

        Contenido a procesar:
        ---------------------
        {content}

        Responde de manera clara y concisa en el idioma y formato solicitado.
        """
        ),
    }

    return [system, user]


def call_gemini_generate(messages, model: str = "gemini-2.5-flash"):
    """Ejecuta la llamada a la API de Gemini."""
    client = initialize_genai()

    system_content = messages[0]["content"] if messages and isinstance(messages, list) else ""
    user_content = messages[1]["content"] if len(messages) > 1 else ""
    prompt_text = system_content + "\n\n" + user_content

    response = client.models.generate_content(
        model=model,
        contents=prompt_text,
    )

    text = getattr(response, "text", None)
    if text is None:
        text = str(response)

    return text.strip()


def extract_text_from_file(file_path: str) -> str:
    """Extrae texto de archivos en diferentes formatos."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"El archivo {file_path} no existe")

    # Archivos de texto plano
    if file_path.suffix in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Archivos PDF
    elif file_path.suffix == ".pdf":
        if PyPDF2 is None:
            raise RuntimeError(
                "La librería 'PyPDF2' no está instalada. Instálala con: "
                "pip install PyPDF2"
            )
        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text.strip()

    else:
        raise ValueError(f"Formato de archivo no soportado: {file_path.suffix}")


# Rutas (Endpoints)
@app.get("/", tags=["Info"])
async def root():
    """Endpoint raíz - sirve la interfaz HTML."""
    index_path = Path(__file__).parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return {
        "mensaje": "Bienvenido a CueBot LLM",
        "endpoints": {
            "POST /procesar-texto": "Procesa texto directo",
            "POST /procesar-archivo-upload": "Procesa archivo cargado",
        },
    }


@app.post("/procesar-texto", tags=["Procesamiento"])
async def procesar_texto(request: TextRequest):
    """
    Procesa texto directo y retorna la respuesta del LLM.

    """
    try:
        if not request.text:
            raise ValueError("El texto no puede estar vacío")

        messages = build_messages(request.text, request.instruction)
        response = call_gemini_generate(messages, model=request.model)

        return JSONResponse(
            status_code=200,
            content={
                "exitoso": True,
                "instruccion": request.instruction,
                "respuesta": response,
                "modelo": request.model,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.post("/procesar-archivo-upload", tags=["Procesamiento"])
async def procesar_archivo_upload(
    file: UploadFile = File(...),
    instruction: str = Form(...),
    model: str = Form("gemini-2.5-flash"),
):
    """
    Procesa un archivo cargado directamente.

    """
    try:
        # Validar tipo de archivo
        if file.filename is None:
            raise ValueError("El nombre del archivo no es válido")

        allowed_extensions = [".txt", ".md", ".pdf"]
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise ValueError(
                f"Tipo de archivo no soportado: {file_ext}. "
                f"Permitidos: {', '.join(allowed_extensions)}"
            )

        # Leer contenido del archivo
        content = await file.read()

        # Decodificar según el tipo
        if file_ext == ".pdf":
            if PyPDF2 is None:
                raise RuntimeError(
                    "La librería 'PyPDF2' no está instalada. Instálala con: "
                    "pip install PyPDF2"
                )
            import io

            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            texto = ""
            for page in pdf_reader.pages:
                texto += page.extract_text()
        else:
            texto = content.decode("utf-8")

        if not texto:
            raise ValueError("El archivo está vacío")

        # Procesar con el LLM
        messages = build_messages(texto, instruction)
        response = call_gemini_generate(messages, model=model)

        return JSONResponse(
            status_code=200,
            content={
                "exitoso": True,
                "archivo": file.filename,
                "tamaño_bytes": len(content),
                "instruccion": instruction,
                "respuesta": response,
                "modelo": model,
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# Punto de entrada
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Iniciando API REST LLM con FastAPI")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
