"""
Tesseract OCR Module - Hybrid Approach
Uses FREE Tesseract OCR + GPT-4o mini (text-only) for cost optimization
Falls back to Vision API if Tesseract fails
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. Install with: pip install pytesseract")

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_openai_client() -> OpenAI:
    """Initialize and return OpenAI client"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=OPENAI_API_KEY)


def extract_text_with_tesseract(image_path: str) -> str:
    """
    Extract raw text from image using FREE Tesseract OCR
    Cost: $0 (completely free)

    Args:
        image_path: Path to the image file

    Returns:
        Extracted text string (empty if extraction fails)
    """
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract not available, skipping OCR")
        return ""

    try:
        logger.info(f"Extracting text with Tesseract from: {image_path}")

        # Open image
        image = Image.open(image_path)

        # Tesseract configuration for better accuracy
        # --psm 6: Assume a single uniform block of text
        # -l spa+eng: Spanish + English languages
        config = '--psm 6 -l spa+eng'

        # Extract text
        text = pytesseract.image_to_string(image, config=config)

        # Clean whitespace
        text = text.strip()

        if text:
            logger.info(f"✓ Tesseract extracted {len(text)} characters")
            logger.debug(f"Extracted text preview: {text[:200]}...")
        else:
            logger.warning("Tesseract extracted empty text")

        return text

    except Exception as e:
        logger.error(f"Tesseract extraction failed: {e}")
        return ""


def structure_text_with_gpt(
    raw_text: str,
    document_type: str,
    fields_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use GPT-4o mini (TEXT-ONLY, no vision) to structure OCR text into JSON
    This is MUCH cheaper than vision API: ~$0.00003 vs ~$0.0002

    Args:
        raw_text: Raw text extracted by Tesseract
        document_type: Type of document (DODA, Manifest, Prefile, Plate)
        fields_schema: Expected JSON schema

    Returns:
        Structured data as dictionary
    """
    client = get_openai_client()

    # Create prompt for text-only structuring
    prompt = f"""Extrae y estructura los siguientes datos del texto OCR de un documento {document_type}.

Texto OCR:
{raw_text}

Responde EXACTAMENTE con este formato JSON:
{fields_schema}

Si no encuentras algún dato en el texto, usa "NO_ENCONTRADO" para strings o 0 para números.
Responde SOLO con el JSON, sin texto adicional."""

    try:
        logger.info(f"Structuring {document_type} text with GPT (text-only mode)...")

        # Text-only API call (NO VISION)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=300,
            temperature=0.1,
            response_format={"type": "json_object"}
        )

        # Parse response
        import json
        result = json.loads(response.choices[0].message.content)

        logger.info(f"✓ Successfully structured {document_type} data with GPT text-only")

        return result

    except Exception as e:
        logger.error(f"GPT text structuring failed: {e}")
        raise


def extract_data_hybrid(
    image_path: str,
    document_type: str,
    fields_schema: Dict[str, Any],
    vision_fallback_func: Optional[callable] = None
) -> Dict[str, Any]:
    """
    HYBRID APPROACH: Tesseract (free) + GPT text-only (cheap)
    Falls back to Vision API if Tesseract fails

    Process:
    1. Try Tesseract OCR (FREE) to extract raw text
    2. If successful, use GPT text-only (~$0.00003) to structure
    3. If Tesseract fails, fallback to Vision API (~$0.0002)

    This approach saves ~93% on cost when Tesseract works!

    Args:
        image_path: Path to image file
        document_type: Type of document
        fields_schema: Expected JSON schema
        vision_fallback_func: Function to call if Tesseract fails

    Returns:
        Extracted and structured data
    """
    logger.info(f"=" * 60)
    logger.info(f"HYBRID EXTRACTION: {document_type}")
    logger.info(f"=" * 60)

    # Step 1: Try FREE Tesseract OCR
    raw_text = extract_text_with_tesseract(image_path)

    # Step 2: If Tesseract succeeded, use cheap text-only GPT
    if raw_text and len(raw_text) > 50:  # Minimum text length threshold
        try:
            logger.info(f"✓ Tesseract successful, using GPT text-only mode (COST SAVINGS: ~93%)")
            return structure_text_with_gpt(raw_text, document_type, fields_schema)

        except Exception as e:
            logger.warning(f"GPT text structuring failed: {e}")
            # Continue to fallback

    # Step 3: Fallback to Vision API if Tesseract failed or text too short
    logger.warning(f"Tesseract failed or insufficient text, falling back to Vision API")

    if vision_fallback_func:
        logger.info("Using Vision API fallback...")
        return vision_fallback_func(image_path)
    else:
        raise Exception(f"Tesseract extraction failed and no fallback provided for {document_type}")


# Example usage schemas for each document type

DODA_SCHEMA = """{
  "fecha_emision": "YYYY-MM-DD",
  "seccion_aduanera": "string"
}"""

MANIFEST_SCHEMA = """{
  "placa_tracto": "string",
  "placa_remolque": "string",
  "nombre_operador": "string",
  "aduana_arribo": "string",
  "numero_entry": "string",
  "broker": "string",
  "descripcion_mercancia": "string",
  "cantidad": number,
  "peso_monto": number
}"""

PREFILE_SCHEMA = """{
  "numero_entry": "string",
  "broker": "string",
  "descripcion_mercancia": "string",
  "cantidad": number,
  "peso_monto": number
}"""

PLATE_SCHEMA = """{
  "plate_number": "string",
  "confidence": number
}"""
