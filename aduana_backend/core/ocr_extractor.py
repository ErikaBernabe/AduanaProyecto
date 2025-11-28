"""
OCR Data Extraction Module
Uses OpenAI's GPT-4 Vision API to extract structured data from document images
"""

import os
import base64
import json
import logging
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

from models.schemas import (
    ExtractedDODAData,
    ExtractedManifestData,
    ExtractedPrefileData,
    ExtractedPlateData,
    AllExtractedData
)

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def get_openai_client() -> OpenAI:
    """
    Initialize and return OpenAI client

    Returns:
        OpenAI client instance

    Raises:
        ValueError: If API key is not configured
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    return OpenAI(api_key=OPENAI_API_KEY)


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string

    Args:
        image_path: Path to the image file

    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_doda_prompt() -> str:
    """
    Create the prompt for extracting data from DODA document

    Returns:
        Prompt string for DODA extraction
    """
    return """Analiza este documento DODA (Declaración de Operación de Despacho Aduanero) y extrae la siguiente información EXACTAMENTE en formato JSON.

IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON, sin texto adicional antes o después.

Campos requeridos:
- fecha_emision: Fecha de emisión del documento en formato YYYY-MM-DD
- seccion_aduanera: Sección aduanera (ciudad/puerto)

Formato de respuesta (SOLO JSON):
{
  "fecha_emision": "YYYY-MM-DD",
  "seccion_aduanera": "string"
}

Si no encuentras algún dato, usa "NO_ENCONTRADO" como valor."""


def create_manifest_prompt() -> str:
    """
    Create the prompt for extracting data from E-Manifest document

    Returns:
        Prompt string for E-Manifest extraction
    """
    return """Analiza este documento E-Manifest (Manifiesto Electrónico) y extrae la siguiente información EXACTAMENTE en formato JSON.

IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON, sin texto adicional antes o después.

INSTRUCCIONES ESPECIALES DE PLACAS:
- Busca la seccion etiquetada como "Plate(s)".
- Es posible que haya multiples placas listadas en varias lineas.
- Identifica cual corresponde al tracto (generalmente placas de USA o asociadas a "Conveyance") y cual al remolque (generalmente placas de MX o asociadas a "Equipment").
- Si hay dudas, extre la primera placa visible placa_tracto y la segunda como placa_remolque. 

Campos requeridos:
- placa_tracto: Número de placa del tracto/camión
- placa_remolque: Número de placa del remolque/trailer
- nombre_operador: Nombre completo del conductor/operador
- aduana_arribo: Aduana de arribo/destino
- numero_entry: Número de entry/entrada
- broker: Nombre del broker/agente aduanal
- descripcion_mercancia: Descripción de la mercancía
- cantidad: Cantidad numérica (solo el número, sin unidades)
- peso_monto: Peso o monto (solo el número, sin unidades ni símbolos)

Formato de respuesta (SOLO JSON):
{
  "placa_tracto": "string",
  "placa_remolque": "string",
  "nombre_operador": "string",
  "aduana_arribo": "string",
  "numero_entry": "string",
  "broker": "string",
  "descripcion_mercancia": "string",
  "cantidad": number,
  "peso_monto": number
}

Si no encuentras algún dato, usa "NO_ENCONTRADO" para strings o 0 para números."""


def create_prefile_prompt() -> str:
    """
    Create the prompt for extracting data from Prefile document

    Returns:
        Prompt string for Prefile extraction
    """
    return """Analiza este documento Prefile (Pre-declaración) y extrae la siguiente información EXACTAMENTE en formato JSON.

IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON, sin texto adicional antes o después.

Campos requeridos:
- numero_entry: Número de entry/entrada
- broker: Nombre del broker/agente aduanal
- descripcion_mercancia: Descripción de la mercancía
- cantidad: Cantidad numérica (solo el número, sin unidades)
- peso_monto: Peso o monto (solo el número, sin unidades ni símbolos)

Formato de respuesta (SOLO JSON):
{
  "numero_entry": "string",
  "broker": "string",
  "descripcion_mercancia": "string",
  "cantidad": number,
  "peso_monto": number
}

Si no encuentras algún dato, usa "NO_ENCONTRADO" para strings o 0 para números."""


def create_plate_prompt() -> str:
    """
    Create the prompt for extracting license plate number from photo

    Returns:
        Prompt string for plate extraction
    """
    return """Analiza esta foto de placa vehicular y extrae el número de placa EXACTAMENTE en formato JSON.

IMPORTANTE: Responde ÚNICAMENTE con el objeto JSON, sin texto adicional antes o después.

Campos requeridos:
- plate_number: Número de placa (letras y números como aparecen)
- confidence: Tu nivel de confianza en la lectura (0.0 a 1.0)

Formato de respuesta (SOLO JSON):
{
  "plate_number": "string",
  "confidence": number
}

Si no puedes leer la placa claramente, usa "NO_LEGIBLE" y confidence menor a 0.5."""


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    """
    Extract and parse JSON from OpenAI response, handling markdown code blocks

    Args:
        response_text: Raw response text from OpenAI

    Returns:
        Parsed JSON object

    Raises:
        ValueError: If JSON cannot be extracted or parsed
    """
    # Remove markdown code blocks if present
    text = response_text.strip()

    # Remove ```json and ``` markers
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Parse JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Response text: {text}")
        raise ValueError(f"Invalid JSON in API response: {e}")


def call_openai_vision_api(
    image_path: str,
    prompt: str,
    max_retries: int = MAX_RETRIES,
    retry_delay: int = RETRY_DELAY
) -> Dict[str, Any]:
    """
    Call OpenAI Vision API with retry logic

    Args:
        image_path: Path to the image file
        prompt: Extraction prompt
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Extracted data as dictionary

    Raises:
        Exception: If all retry attempts fail
    """
    client = get_openai_client()

    # Encode image
    base64_image = encode_image_to_base64(image_path)

    for attempt in range(max_retries):
        try:
            logger.info(f"Calling OpenAI API (attempt {attempt + 1}/{max_retries})...")

            # Call GPT-4 Vision API
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # High detail for accurate text extraction from complex documents
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,  # Reduced from 1000 to 300 for cost optimization
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}  # Force JSON response for better parsing
            )

            # Extract response text
            response_text = response.choices[0].message.content
            logger.info(f"Received response from OpenAI")

            # Parse JSON from response
            extracted_data = extract_json_from_response(response_text)

            logger.info(f"Successfully extracted data: {json.dumps(extracted_data, ensure_ascii=False)}")

            return extracted_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"Failed to parse valid JSON after {max_retries} attempts: {e}")

        except Exception as e:
            logger.error(f"API call error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise Exception(f"OpenAI API call failed after {max_retries} attempts: {e}")

    raise Exception(f"Failed to extract data after {max_retries} attempts")


def extract_doda_data(image_path: str) -> ExtractedDODAData:
    """
    Extract data from DODA document

    Args:
        image_path: Path to the DODA image file

    Returns:
        ExtractedDODAData object
    """
    logger.info(f"Extracting DODA data from: {image_path}")

    prompt = create_doda_prompt()
    data = call_openai_vision_api(image_path, prompt)

    return ExtractedDODAData(**data)


def extract_manifest_data(image_path: str) -> ExtractedManifestData:
    """
    Extract data from E-Manifest document

    Args:
        image_path: Path to the E-Manifest image file

    Returns:
        ExtractedManifestData object
    """
    logger.info(f"Extracting E-Manifest data from: {image_path}")

    prompt = create_manifest_prompt()
    data = call_openai_vision_api(image_path, prompt)

    return ExtractedManifestData(**data)


def extract_prefile_data(image_path: str) -> ExtractedPrefileData:
    """
    Extract data from Prefile document

    Args:
        image_path: Path to the Prefile image file

    Returns:
        ExtractedPrefileData object
    """
    logger.info(f"Extracting Prefile data from: {image_path}")

    prompt = create_prefile_prompt()
    data = call_openai_vision_api(image_path, prompt)

    return ExtractedPrefileData(**data)


def extract_plate_data(image_path: str) -> ExtractedPlateData:
    """
    Extract license plate number from photo

    Args:
        image_path: Path to the plate image file

    Returns:
        ExtractedPlateData object
    """
    logger.info(f"Extracting plate data from: {image_path}")

    prompt = create_plate_prompt()
    data = call_openai_vision_api(image_path, prompt)

    return ExtractedPlateData(**data)


def extract_all_documents_unified(
    doda_path: str,
    manifest_path: str,
    prefile_path: str,
    tractor_plate_path: str,
    trailer_plate_path: str
) -> AllExtractedData:
    """
    OPTIMIZED: Extract data from ALL 5 images in a SINGLE API call
    This reduces cost by ~80% and latency by ~75% compared to 5 separate calls

    Args:
        doda_path: Path to DODA document image
        manifest_path: Path to E-Manifest document image
        prefile_path: Path to Prefile document image
        tractor_plate_path: Path to tractor plate photo
        trailer_plate_path: Path to trailer plate photo

    Returns:
        AllExtractedData object with all extracted data

    Raises:
        Exception: If extraction fails
    """
    logger.info("=" * 70)
    logger.info("UNIFIED EXTRACTION: Processing all 5 images in a single API call")
    logger.info("=" * 70)

    client = get_openai_client()

    # Encode all 5 images to base64
    logger.info("Encoding 5 images to base64...")
    images_b64 = {
        'doda': encode_image_to_base64(doda_path),
        'manifest': encode_image_to_base64(manifest_path),
        'prefile': encode_image_to_base64(prefile_path),
        'tractor': encode_image_to_base64(tractor_plate_path),
        'trailer': encode_image_to_base64(trailer_plate_path)
    }
    logger.info("✓ All images encoded successfully")

    # Create unified prompt that extracts ALL data in one response
    unified_prompt = """Analiza estas 5 imágenes de documentos aduanales y extrae TODA la información en UN SOLO objeto JSON.

Imágenes en orden:
1. DODA (Declaración de Operación de Despacho Aduanero)
2. E-Manifest (Manifiesto Electrónico)
3. Prefile (Pre-declaración)
4. Foto de placa del tracto
5. Foto de placa del remolque

Extrae EXACTAMENTE estos campos en formato JSON (sin texto adicional antes o después):

{
  "doda": {
    "fecha_emision": "YYYY-MM-DD",
    "seccion_aduanera": "string"
  },
  "manifest": {
    "placa_tracto": "string",
    "placa_remolque": "string",
    "nombre_operador": "string",
    "aduana_arribo": "string",
    "numero_entry": "string",
    "broker": "string",
    "descripcion_mercancia": "string",
    "cantidad": number,
    "peso_monto": number
  },
  "prefile": {
    "numero_entry": "string",
    "broker": "string",
    "descripcion_mercancia": "string",
    "cantidad": number,
    "peso_monto": number
  },
  "tractor_plate": {
    "plate_number": "string",
    "confidence": number
  },
  "trailer_plate": {
    "plate_number": "string",
    "confidence": number
  }
}

Reglas:
- Si no encuentras algún dato: usa "NO_ENCONTRADO" para strings, 0 para números, 0.5 para confidence
- Para placas no legibles: usa "NO_LEGIBLE" y confidence < 0.5
- Responde ÚNICAMENTE con el objeto JSON completo"""

    try:
        logger.info("Calling OpenAI API with all 5 images (unified call)...")

        # Single API call with ALL 5 images
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        # Text prompt
                        {"type": "text", "text": unified_prompt},
                        # All 5 images with "high" detail for accurate text extraction
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{images_b64['doda']}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{images_b64['manifest']}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{images_b64['prefile']}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{images_b64['tractor']}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{images_b64['trailer']}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,  # Slightly higher for unified response
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # Extract and parse response
        response_text = response.choices[0].message.content
        logger.info("✓ Received unified response from OpenAI")

        # Parse JSON
        data = extract_json_from_response(response_text)
        logger.info(f"✓ Successfully parsed unified JSON response")

        # Convert to Pydantic models
        extracted_data = AllExtractedData(
            doda=ExtractedDODAData(**data['doda']),
            manifest=ExtractedManifestData(**data['manifest']),
            prefile=ExtractedPrefileData(**data['prefile']),
            tractor_plate=ExtractedPlateData(**data['tractor_plate']),
            trailer_plate=ExtractedPlateData(**data['trailer_plate'])
        )

        logger.info("=" * 70)
        logger.info("✓ UNIFIED EXTRACTION COMPLETE - All data extracted successfully")
        logger.info("=" * 70)

        return extracted_data

    except Exception as e:
        logger.error(f"Unified extraction failed: {e}", exc_info=True)
        raise Exception(f"Failed to extract data from all documents: {str(e)}")
