# Sprint1/conversacion_2.py
import os
import sys
import textwrap
from datetime import datetime

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

# Path al archivo PDF
PDF_PATH = os.path.join(os.path.dirname(__file__), "cuento.pdf")
# Path para guardar la conversación
CONVERSATION_PATH = os.path.join(
    os.path.dirname(__file__), "conversacion_2.txt"
)


def read_pdf(path: str) -> str:
    """Lee el contenido completo del archivo PDF."""
    if PyPDF2 is None:
        raise RuntimeError(
            "La librería 'PyPDF2' no está instalada. Instálala con: "
            "pip install PyPDF2"
        )

    try:
        text = ""
        with open(path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            print(f"Leyendo PDF: {num_pages} páginas detectadas...")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"

        return text.strip()
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo PDF: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        sys.exit(1)


def get_story_bullet_points(
    story_text: str, model: str = "gemini-2.5-flash"
) -> str:
    """Obtiene 5 puntos clave de la historia usando el LLM."""
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

    prompt = textwrap.dedent(
        f"""
        Analiza la siguiente historia y proporciona exactamente 5 viñetas (bullet points)
        que presenten los elementos más importantes de la trama. Cada viñeta debe ser
        concisa pero informativa.

        Historia:
        ---------------------
        {story_text}
        ---------------------

        Responde solamente con las 5 viñetas en formato:
        • Viñeta 1
        • Viñeta 2
        • Viñeta 3
        • Viñeta 4
        • Viñeta 5
        """
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if text is None:
        text = str(response)

    return text.strip()


def call_gemini_generate(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Ejecuta la llamada a la API de Gemini."""
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

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if text is None:
        text = str(response)

    return text.strip()


def save_conversation(conversation: list, path: str) -> None:
    """Guarda la conversación en un archivo de texto."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            for exchange in conversation:
                f.write(f"Usuario: {exchange['user']}\n")
                f.write(f"LLM: {exchange['llm']}\n")
                f.write("\n")
        print(f"\nConversación guardada en: {path}")
    except Exception as e:
        print(f"Error al guardar la conversación: {e}")


def main():
    """Función principal del script."""
    # Validar dependencias
    if genai is None:
        print("La librería 'google.genai' no está instalada. Instálala con:")
        print("  pip install google-genai")
        return

    if load_dotenv is None:
        print("La librería 'python-dotenv' no está instalada. Instálala con:")
        print("  pip install python-dotenv")
        return

    if PyPDF2 is None:
        print("La librería 'PyPDF2' no está instalada. Instálala con:")
        print("  pip install PyPDF2")
        return

    print("=" * 60)
    print("CONVERSACIÓN 2: Análisis de Historia con LLM")
    print("=" * 60)
    print("\nLeyendo el archivo PDF...")

    story_text = read_pdf(PDF_PATH)
    print(f"PDF leído exitosamente ({len(story_text)} caracteres)")

    print("\nGenerando 5 viñetas de la historia...")
    bullet_points = get_story_bullet_points(story_text)

    conversation = []

    user_prompt_1 = (
        "Crea 5 viñetas que presenten los elementos más importantes de la historia "
        "contenida en el archivo 'cuento.pdf' (usando el texto de todas las páginas "
        "del archivo)."
    )

    conversation.append(
        {
            "user": user_prompt_1,
            "llm": bullet_points,
        }
    )

    print("\n--- Viñetas de la Historia ---\n")
    print(bullet_points)

    save_conversation(conversation, CONVERSATION_PATH)

    print("\n" + "=" * 60)
    print("Script completado exitosamente")
    print("=" * 60)


if __name__ == "__main__":
    main()
