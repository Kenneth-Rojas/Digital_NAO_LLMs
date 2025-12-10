# Sprint 1: Interacción con LLM

## Descripción General

Este sprint contiene dos scripts en Python que demuestran la interacción con modelos de lenguaje de gran escala (LLM) mediante la API de Google GenAI. Los scripts permiten procesar y analizar contenido textual (documentos TXT y PDF) mediante prompts diseñados para obtener resúmenes y extracciones de información relevante.

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Una clave API válida de Google GenAI (obtenerla en [Google AI Studio](https://aistudio.google.com))

---

## 📋 Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone https://github.com/Kenneth-Rojas/Digital_NAO_LLMs.git
cd Digital_NAO_LLMs/Sprint1
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

### 4. Configurar la clave API

Crea un archivo `.env` en la raíz del proyecto con tu clave API:

```bash
echo "GOOGLE_API_KEY=tu_clave_api_aqui" > .env
```

O crea el archivo manualmente:

```
GOOGLE_API_KEY=tu_clave_api_aqui
```

---

## 🚀 Ejecución de los Scripts

### Script 1: `conversacion_1.py`

#### ¿Qué hace?

Este script procesa un artículo de noticias sobre banca digital (`news_digital_bank.txt`) mediante prompts que solicitan:

1. **Resumen en español**: Genera un resumen de exactamente 2 párrafos del contenido del artículo.
2. **Información adicional**: Añade un tercer párrafo que indica:
   - La fuente/diario del que proviene la noticia
   - El título correspondiente de la noticia

#### Cómo ejecutar:

```bash
python conversacion_1.py
```
---

### Script 2: `conversacion_2.py`

#### ¿Qué hace?

Este script procesa un archivo PDF (`cuento.pdf`) mediante prompts que solicitan:

1. **Extracción de puntos clave**: Crea 5 viñetas que presenten los elementos más importantes de la historia contenida en el archivo PDF.
2. **Procesamiento multicapa**: Lee todas las páginas del PDF y analiza el contenido completo.

#### Cómo ejecutar:

```bash
python conversacion_2.py
```

---

## 📝 Notas Importantes

1. **Clave API**: Nunca compartas tu clave API en repositorios públicos. Usa un archivo `.env` local.
2. **Cuotas de uso**: Ten en cuenta los límites de la API gratuita de Google GenAI.
3. **Archivos de entrada**: Asegúrate de que `news_digital_bank.txt` y `cuento.pdf` existan antes de ejecutar los scripts.
4. **Encoding**: Los scripts usan UTF-8 para garantizar soporte completo de caracteres en español.

---


## 👨‍💻 Autor

Kenneth Rojas - [GitHub](https://github.com/Kenneth-Rojas)

---

**Última actualización**: Diciembre 2025
