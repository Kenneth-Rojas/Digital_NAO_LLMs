"""
Ejemplo 4: Draft de la interfaz grafica para CueBot
Conectado con la API LLM de Gemini
"""

import gradio as gr
from PyPDF2 import PdfReader
import random
import time
import requests
import json


# Variable auxiliar para guardar el texto del PDF
CORPUS_TEXT = ''

# URL de la API
API_URL = "http://localhost:8000/generate"


def add_text(history, text):
    """
    Agrega texto a la historia del chat y actualiza la
    interfaz
    """

    history = history or []
    history.append({"role": "user", "content": text})

    return history, gr.update(value="", interactive=False)


def add_file(history, file):
    """
    Permite agrega un texto pdf a la conversacion del chat
    y guardar 
    """
    # agrega el nombre del archivo al Chat (formato esperado por Gradio)
    history = history or []
    history.append({"role": "user", "content": f"Archivo subido: {file.name}"})

    # Leemos el texto del archivo PDF y lo guardamos en
    # CORPUS_TEXT para el futuro

    # Abre el archivo PDF en modo lectura binaria
    with open(file.name, 'rb') as pdf_file:
        # Crea un lector de PDF
        pdf_reader = PdfReader(pdf_file)

        # Inicializa una variable para almacenar el texto extraído
        extracted_text = ""

        # Itera sobre todas las páginas del PDF y extrae el texto
        for page_num in range(len(pdf_reader.pages)):
            extracted_text += pdf_reader.pages[page_num].extract_text()

        # Comunica el texto recien leido a la variable global CORPUS_TEXT
        global CORPUS_TEXT
        CORPUS_TEXT = extracted_text
        print(CORPUS_TEXT)
    return history


def bot(history):
    """
    Obtiene la respuesta del Bot desde la API
    """
    history = history or []

    # Encuentra el último mensaje de usuario
    # Suponemos que el último elemento es el mensaje del usuario que disparó la llamada
    user_msg = None
    if history:
        last = history[-1]
        if isinstance(last, dict) and last.get("role") == "user":
            user_msg = last.get("content")

    if user_msg is None:
        # Nothing to do
        return history

    # Añade un mensaje del asistente vacío para mostrar la respuesta
    history.append({"role": "assistant", "content": ""})
    assistant_index = len(history) - 1

    try:
        # Prepara la solicitud para el API
        payload = {
            "instruction": user_msg,
            "fragments": CORPUS_TEXT if CORPUS_TEXT else None,
            "model": "gemini-2.5-flash"
        }
        
        # Realiza la llamada al API
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        # Extrae la respuesta
        result = response.json()
        response_text = result.get("output", "Error: No se recibió respuesta del API")
        
    except requests.exceptions.ConnectionError:
        response_text = "Error: No se puede conectar con el API. Asegúrate de que está ejecutándose en http://localhost:8000"
    except requests.exceptions.Timeout:
        response_text = "Error: La solicitud al API tardó demasiado tiempo"
    except Exception as e:
        response_text = f"Error al comunicarse con el API: {str(e)}"
    
    # Genera el efecto de escribir lento con una pausa
    # Como si el texto se generara lentamente
    for character in response_text:
        history[assistant_index]["content"] += character
        time.sleep(0.02)
        yield history



# Crea la aplicacion de Gradio
with gr.Blocks() as demo:

    # Crea ek chatbot
    chatbot = gr.Chatbot([], elem_id="chatbot", height=750)


    with gr.Row():

        # Cuadro de texto de conversacion
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder="Especifica el archivo pdf o ingresa un texto",
                container=False
            )

        # Cuadro de subida de archivo
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.UploadButton("📁 Subir Archivo:", file_types=[".pdf"])

    # Controlador de acciones para retroalimentar al bot
    # Con su respuesta
    txt_msg = txt.submit(
        fn=add_text,
        inputs=[chatbot, txt],
        outputs=[chatbot, txt],
        queue=False
        ).success(
        fn=bot,
        inputs=chatbot,
        outputs=chatbot
    )

    # Actualiza la convesacion con el texto generado
    txt_msg.success(
        fn=lambda: gr.update(interactive=True),
        inputs=None,
        outputs=[txt],
        queue=False
        )

    # Sube el archivo  y actualiza la conversacion
    file_msg = btn.upload(
        fn=add_file,
        inputs=[chatbot, btn],
        outputs=[chatbot],
        queue=False).success(
        bot, chatbot, chatbot
    )


demo.queue()
if __name__ == "__main__":
    demo.launch(
    share=True
    )
