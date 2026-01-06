from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, List, Union, Optional
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
import re
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
    # Accept any type for instruction (string, list, dict, etc.) to avoid 422 errors
    instruction: Optional[Any] = None
    # Accept any type for fragments (string, list, dict, etc.) to avoid 422 errors
    fragments: Optional[Any] = None
    model: Optional[str] = "gemini-2.5-flash"

app = FastAPI(title="Cuebot LLM API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log body and validation errors to stdout for easier debugging
    body = await request.body()
    print("RequestValidationError: body=", body[:200])
    print("RequestValidationError: errors=", exc.errors())
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body.decode(errors="replace")[:10000],
        },
    )




def build_prompt(instruction: str, fragments: Optional[Union[str, List[str]]]) -> str:
    system = (
        "Eres un asistente experto análisis de texto. "
        "Responde con precisión en español y mantén un tono neutral."
    )

    # Normalize fragments into a printable text block
    if isinstance(fragments, list):
        fragments_text = "\n\n".join(str(f) for f in fragments)
    elif fragments is None:
        fragments_text = ""
    else:
        fragments_text = str(fragments)

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


def _simple_local_generate(instruction: str, fragments_text: Optional[str]) -> str:
    """
    Lightweight local generator to answer simple questions or produce a short summary
    from provided fragments when no external LLM is available.
    """
    if not fragments_text:
        return "No hay fragmentos de texto disponibles para analizar. Sube un PDF primero."

    # Normalize fragments into plain text
    text = re.sub(r"\s+", " ", fragments_text.strip())

    # If the instruction asks for a resumen/summary, return the first ~800 chars as a summary
    if re.search(r"resumen|resume|resumir|sumario|summary", instruction, re.IGNORECASE):
        snippet = text[:800]
        return f"Resumen (generado localmente): {snippet}"

    # If it's a question, try to find most relevant sentences
    # Extract sentences
    sentences = re.split(r"(?<=[\.\?\!])\s+", text)

    # Extract keywords from the instruction (naive)
    words = [w.lower() for w in re.findall(r"\w+", instruction) if len(w) > 3]
    if not words:
        # fallback: return a short context window
        return text[:1000]

    # Score sentences by occurrences of keywords
    def score_sentence(s: str) -> int:
        s_low = s.lower()
        return sum(s_low.count(k) for k in words)

    scored = [(score_sentence(s), s) for s in sentences]
    scored.sort(reverse=True, key=lambda x: x[0])

    best = [s for sc, s in scored if sc > 0]
    if not best:
        # If no sentence matched, return a short extract and say we couldn't find direct answer
        extract = " ".join(sentences[:3])
        return (
            "No pude encontrar una respuesta directa en el texto. Aquí hay un extracto relevante: "
            + extract[:1000]
        )

    # Return the top matching sentences (up to 3)
    answer = " ".join(best[:3])
    return f"Respuesta (generada localmente usando el texto proporcionado): {answer}"


def call_gemini_generate(prompt_text: str, model: str = "gemini-2.5-flash", fragments: Optional[str] = None) -> str:
    """
    Try to call Google GenAI if available; otherwise fallback to a simple local generator.
    If genai raises an unexpected error, fall back to local generator as well.
    """
    # Prefer external GenAI if available
    if genai is None:
        return _simple_local_generate(prompt_text, fragments)

    # Ensure dotenv is available (safe to call if it is)
    if load_dotenv:
        load_dotenv()

    api_key = os.environ.get("GENAI_API_KEY")
    try:
        try:
            if api_key:
                client = genai.Client(api_key=api_key)
            else:
                client = genai.Client()
        except TypeError:
            client = genai.Client()

        # Attempt to call the GenAI API; if it fails, fallback to local generator
        response = client.models.generate_content(model=model, contents=prompt_text)
        text = getattr(response, "text", None)
        if text is None:
            text = str(response)

        return text.strip()
    except Exception:
        # On any error, return a local-generated answer using fragments (if present)
        return _simple_local_generate(prompt_text, fragments)


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        # Normalize instruction (clients may send a list/dict from Gradio)
        raw_instruction = req.instruction
        if isinstance(raw_instruction, list):
            parts = []
            for it in raw_instruction:
                if isinstance(it, str):
                    parts.append(it)
                elif isinstance(it, dict):
                    for k in ("text", "content", "value"):
                        if k in it and isinstance(it[k], str):
                            parts.append(it[k])
                            break
                    else:
                        parts.append(str(it))
                else:
                    parts.append(str(it))
            instruction_text = " ".join(parts).strip()
        elif isinstance(raw_instruction, dict):
            for k in ("text", "content", "value"):
                if k in raw_instruction and isinstance(raw_instruction[k], str):
                    instruction_text = raw_instruction[k]
                    break
            else:
                instruction_text = str(raw_instruction)
        elif raw_instruction is None:
            instruction_text = ""
        else:
            instruction_text = str(raw_instruction)

        print("/generate called. instruction type:", type(raw_instruction), "normalized length:", len(instruction_text))
        print("/generate called. fragments type:", type(req.fragments))

        # Normalize fragments to a single text string to pass to the generator
        if isinstance(req.fragments, list):
            fragments_text = "\n\n".join(str(f) for f in req.fragments)
        elif req.fragments is None:
            fragments_text = None
        else:
            fragments_text = str(req.fragments)

        # Build prompt using normalized instruction text
        try:
            prompt = build_prompt(instruction_text, fragments_text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error construyendo el prompt: {e}")

        output = call_gemini_generate(prompt, model=req.model, fragments=fragments_text)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación: {e}")

    return {"output": output}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
