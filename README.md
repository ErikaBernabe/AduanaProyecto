# 🚛 Crucero Fronterizo - Sistema de Validación Documental

Aplicación web para digitalizar, escanear (OCR) y validar documentos de exportación (DODA, E-Manifest, Prefile) y placas vehiculares antes del cruce fronterizo. El sistema utiliza Inteligencia Artificial para extraer datos y validar la consistencia de la información.

## 🛠 Tecnologías Utilizadas

### Frontend (Cliente)

- **React**: Librería principal de UI.
- **React Hook Form**: Manejo de formularios.
- **React Icons**: Iconografía.
- **React Toastify**: Notificaciones al usuario.
- **Axios/Fetch**: Comunicación con el API.

### Backend (Servidor)

- **Python 3.11**: Lenguaje base (Versión 3.11 requerida por compatibilidad).
- **FastAPI**: Framework para el API REST.
- **Uvicorn**: Servidor ASGI.
- **OpenAI GPT-4 Vision**: Motor de OCR y extracción de datos.
- **Pillow**: Procesamiento de imágenes.

---

## 🚀 Guía de Instalación y Ejecución

Para correr el proyecto localmente, necesitas dos terminales abiertas: una para el Frontend y otra para el Backend.

### 1. Configuración del Backend (Python)

> **Nota Importante:** Este proyecto requiere **Python 3.11** para evitar conflictos con la librería `Pillow`.

1.  Navega a la carpeta del backend:

    ```bash
    cd aduana_backend
    ```

2.  Crea y activa un entorno virtual:

    ```bash
    # Crear el entorno (asegúrate de usar Python 3.11)
    py -3.11 -m venv venv

    # Activar en Windows (Git Bash)
    source venv/Scripts/activate
    # Activar en Windows (CMD/Powershell)
    .\venv\Scripts\activate
    ```

3.  Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4.  Configura las variables de entorno:

    - Crea un archivo `.env` dentro de `aduana_backend`.
    - Agrega tu llave de OpenAI:
      ```
      OPENAI_API_KEY=tu_clave_aqui
      ```

5.  Inicia el servidor:
    ```bash
    python -m uvicorn main:app --reload
    ```
    _El backend correrá en `http://localhost:8000`_

---

### 2. Configuración del Frontend (React)

1.  Navega a la carpeta raíz del proyecto (si estabas en backend, sube un nivel):

    ```bash
    cd ..
    ```

2.  Instala las dependencias de Node:

    ```bash
    npm install
    ```

3.  Inicia la aplicación:
    ```bash
    npm start
    ```
    _El frontend correrá en `http://localhost:3000`_

---

## 📋 Funcionalidades Principales

1.  **Login**: Acceso seguro al sistema.
2.  **Captura de Datos**:
    - Formulario manual para datos del conductor.
    - Captura fotográfica de placas (Tracto y Remolque).
3.  **Digitalización de Documentos**: Carga o fotografía de DODA, E-Manifest y Prefile.
4.  **Validación Inteligente**:
    - Extracción automática de datos usando IA.
    - Cruce de información entre documentos.
    - Validación de placas físicas vs manifiesto.
