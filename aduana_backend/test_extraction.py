"""
Test script for OpenAI data extraction
Creates test images with text to verify OCR functionality
"""

import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import json

def create_test_document_with_text(text_lines: list, size=(800, 600)) -> str:
    """
    Create a test document image with text lines

    Args:
        text_lines: List of text lines to draw on the image
        size: Image size (width, height)

    Returns:
        Base64 data URL of the image
    """
    # Create white image
    img = Image.new('RGB', size, color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Try to use a default font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    # Draw text lines
    y_position = 50
    for line in text_lines:
        draw.text((50, y_position), line, fill=(0, 0, 0), font=font)
        y_position += 40

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return f"data:image/jpeg;base64,{img_base64}"


def create_test_payload():
    """
    Create a test payload with realistic document text
    """
    # DODA document
    doda_text = [
        "DECLARACIÓN DE OPERACIÓN DE DESPACHO ADUANERO",
        "DODA",
        "",
        "Fecha de Emisión: 2025-10-20",
        "Sección Aduanera: Tijuana",
        "Número de Documento: DODA-2025-001234",
    ]

    # E-Manifest document
    manifest_text = [
        "E-MANIFEST / MANIFIESTO ELECTRÓNICO",
        "",
        "Placa Tracto: ABC-123",
        "Placa Remolque: XYZ-789",
        "Operador: Juan Pérez García",
        "Aduana de Arribo: Tijuana",
        "",
        "Entry Number: ENT-2025-001234",
        "Broker: Brokers Unidos S.A.",
        "Mercancía: Productos electrónicos",
        "Cantidad: 100 unidades",
        "Peso/Monto: 5000.50 kg",
    ]

    # Prefile document
    prefile_text = [
        "PREFILE / PRE-DECLARACIÓN",
        "",
        "Entry Number: ENT-2025-001234",
        "Broker: Brokers Unidos S.A.",
        "",
        "Descripción: Productos electrónicos",
        "Cantidad: 100",
        "Peso/Monto: 5000.50",
    ]

    # Tractor plate
    tractor_plate_text = [
        "",
        "",
        "    ABC-123",
        "",
        "   MÉXICO",
    ]

    # Trailer plate
    trailer_plate_text = [
        "",
        "",
        "    XYZ-789",
        "",
        "   MÉXICO",
    ]

    payload = {
        "driverData": {
            "name": "Juan Pérez García",
            "tractorPlate": create_test_document_with_text(tractor_plate_text, (400, 200)),
            "trailerPlate": create_test_document_with_text(trailer_plate_text, (400, 200))
        },
        "documents": {
            "doda": create_test_document_with_text(doda_text),
            "emanifest": create_test_document_with_text(manifest_text, (800, 700)),
            "prefile": create_test_document_with_text(prefile_text)
        }
    }

    return payload


if __name__ == "__main__":
    import requests

    print("=" * 70)
    print("OpenAI Data Extraction Test")
    print("=" * 70)
    print("\nCreating test documents with realistic text...")

    payload = create_test_payload()

    print("✓ Test documents created")
    print(f"  - Driver: {payload['driverData']['name']}")
    print(f"  - Documents: DODA, E-Manifest, Prefile")
    print(f"  - Plates: Tractor, Trailer")

    print("\n" + "=" * 70)
    print("Sending request to /api/validate...")
    print("=" * 70)
    print("\nNOTE: This will make actual OpenAI API calls and may take 30-60 seconds.")
    print("      Press Ctrl+C to cancel if you don't want to proceed.\n")

    try:
        import time
        time.sleep(3)  # Give user time to cancel

        response = requests.post(
            "http://localhost:8000/api/validate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minute timeout for AI processing
        )

        print(f"\nStatus Code: {response.status_code}")
        print("\nResponse:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            print("\n" + "=" * 70)
            print("✅ TEST PASSED - Data extraction successful!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print(f"❌ TEST FAILED - Status {response.status_code}")
            print("=" * 70)

    except requests.exceptions.Timeout:
        print("\n❌ Request timed out. AI processing may take longer than expected.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Is it running on port 8000?")
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
