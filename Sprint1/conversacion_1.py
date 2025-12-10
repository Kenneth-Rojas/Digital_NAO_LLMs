# Sprint1/conversacion_1.py
import os
import sys
import textwrap

try:
    from google import genai
except Exception:
    genai = None

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# Path al archivo de noticias
NEWS_PATH = os.path.join(os.path.dirname(__file__), "news_digital_bank.txt")


def read_news(path: str) -> str:
    """Lee el contenido del archivo de noticias."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: no se encontró el archivo: {path}")
        sys.exit(1)


def build_messages(article_text: str, language: str = "es"):
    """Construye los mensajes para el modelo LLM."""
    system = {
        "role": "system",
        "content": (
            "Eres un asistente experto en periodismo que resume noticias en "
            "español. Responde con precisión, manteniendo el tono informativo "
            "y neutral."
        ),
    }

    user = {
        "role": "user",
        "content": textwrap.dedent(
            f"""
        Según el texto proporcionado, realiza un resumen de la noticia en español 
        de exactamente dos párrafos. Adicionalmente agrega un tercer párrafo con la 
        fuente y el título de la noticia. Si no están disponibles, marcalos con 
        'Desconocido'.

        Texto de la noticia:
        ---------------------
        {article_text}

        Responde solamente con los tres párrafos solicitados (dos de resumen + 
        tercer párrafo con 'Diario:' y 'Título:'). No incluyas explicaciones 
        adicionales.
        """
        ),
    }

    return [system, user]


def call_gemini_generate(messages, model: str = "gemini-2.5-flash"):
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


def main():
    """Función principal del script."""
    article = read_news(NEWS_PATH)
    messages = build_messages(article)

    if genai is None:
        print("La librería 'google.genai' no está instalada. Instálala con:")
        print("  pip install google-genai")
        return

    if load_dotenv is None:
        print("La librería 'python-dotenv' no está instalada. Instálala con:")
        print("  pip install python-dotenv")
        return

    model = "gemini-2.5-flash"
    print("\nLlamando a Gemini... esto puede tardar unos segundos")

    try:
        output = call_gemini_generate(messages, model=model)
    except Exception as e:
        print("Error durante la llamada a Gemini:", e)
        return

    print("\n--- Resultado del LLM (Gemini) ---\n")
    print(output)


if __name__ == "__main__":
    main()
