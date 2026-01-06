from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union, Optional
import os
import textwrap

try:
    from google import genai
except Exception:
    genai = None

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


class GenerateRequest(BaseModel):
    instruction: str
    fragments: Optional[Union[str, List[str]]] = None
    model: Optional[str] = "gemini-2.5-flash"


app = FastAPI(title="Cuebot LLM API")


def build_prompt(instruction: str, fragments: Optional[Union[str, List[str]]]) -> str:
    system = (
        "Eres un asistente experto en periodismo y análisis de texto. "
        "Responde con precisión en español y mantén un tono informativo y neutral."
    )

    if isinstance(fragments, list):
        fragments_text = "\n\n".join(fragments)
    else:
        fragments_text = fragments or ""

    user = textwrap.dedent(
        f"""
        Instrucción para el LLM:
        -----------------------
        {instruction}

        Fragmentos a analizar:
        -----------------------
        {fragments_text}

        Responde en español y proporciona únicamente la respuesta solicitada.
        """
    )

    return system + "\n\n" + user


def call_gemini_generate(prompt_text: str, model: str = "gemini-2.5-flash") -> str:
    if genai is None:
        raise RuntimeError(
            "La librería 'google.genai' no está instalada. Instálala con: pip install google-genai"
        )

    if load_dotenv is None:
        raise RuntimeError(
            "La librería 'python-dotenv' no está instalada. Instálala con: pip install python-dotenv"
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

    response = client.models.generate_content(model=model, contents=prompt_text)
    text = getattr(response, "text", None)
    if text is None:
        text = str(response)

    return text.strip()


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        prompt = build_prompt(req.instruction, req.fragments)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error construyendo el prompt: {e}")

    try:
        output = call_gemini_generate(prompt, model=req.model)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación: {e}")

    return {"output": output}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
