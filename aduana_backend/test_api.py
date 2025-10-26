"""
Test script for the /api/validate endpoint
Creates a minimal test payload to verify the endpoint functionality
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image

def create_test_image(text: str, size=(400, 300)) -> str:
    """
    Create a simple test image with text and return as base64 data URL
    """
    # Create a simple image
    img = Image.new('RGB', size, color=(255, 255, 255))

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=90)
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    # Return as data URL
    return f"data:image/jpeg;base64,{img_base64}"


def test_validate_endpoint():
    """
    Test the /api/validate endpoint with mock data
    """
    # Create test payload
    payload = {
        "driverData": {
            "name": "Juan Pérez García",
            "tractorPlate": create_test_image("Tractor Plate"),
            "trailerPlate": create_test_image("Trailer Plate")
        },
        "documents": {
            "doda": create_test_image("DODA Document"),
            "emanifest": create_test_image("E-Manifest Document"),
            "prefile": create_test_image("Prefile Document")
        }
    }

    print("Testing /api/validate endpoint...")
    print(f"Driver: {payload['driverData']['name']}")
    print("Sending request...\n")

    try:
        # Send POST request
        response = requests.post(
            "http://localhost:8000/api/validate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        # Print response
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        if response.status_code == 200:
            print("\n✅ Test PASSED - Endpoint is working correctly!")
        else:
            print(f"\n❌ Test FAILED - Unexpected status code: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Is it running on port 8000?")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_validate_endpoint()
