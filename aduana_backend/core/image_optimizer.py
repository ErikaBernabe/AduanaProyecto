"""
Image optimization module
Handles decoding, resizing, and compression of base64 images
"""

import base64
import io
import re
from typing import Tuple, Optional
from PIL import Image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Image optimization settings
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
JPEG_QUALITY = 85
PNG_OPTIMIZE = True


def decode_base64_image(base64_string: str) -> Image.Image:
    """
    Decode a base64 data URL string into a PIL Image object

    Args:
        base64_string: Base64 data URL (e.g., "data:image/png;base64,iVBORw0KG...")

    Returns:
        PIL Image object

    Raises:
        ValueError: If the base64 string is invalid or cannot be decoded
    """
    try:
        # Validate format
        if not base64_string.startswith('data:image/'):
            raise ValueError("Invalid data URL format. Must start with 'data:image/'")

        # Extract the base64 data (remove the data URL prefix)
        # Format: data:image/png;base64,ACTUAL_BASE64_DATA
        match = re.match(r'data:image/(?P<format>\w+);base64,(?P<data>.+)', base64_string)

        if not match:
            raise ValueError("Invalid base64 data URL format")

        image_format = match.group('format')
        base64_data = match.group('data')

        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_data)

        # Create PIL Image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary (some formats like RGBA need conversion for JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create a white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')

        logger.info(f"Decoded {image_format} image: {image.size[0]}x{image.size[1]} pixels")

        return image

    except base64.binascii.Error as e:
        logger.error(f"Base64 decoding error: {e}")
        raise ValueError(f"Invalid base64 encoding: {e}")

    except Exception as e:
        logger.error(f"Image decoding error: {e}")
        raise ValueError(f"Failed to decode image: {e}")


def resize_image(image: Image.Image, max_width: int = MAX_WIDTH, max_height: int = MAX_HEIGHT) -> Image.Image:
    """
    Resize an image while maintaining aspect ratio

    Args:
        image: PIL Image object
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels

    Returns:
        Resized PIL Image object
    """
    try:
        original_size = image.size

        # Calculate new dimensions maintaining aspect ratio
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        new_size = image.size

        if original_size != new_size:
            logger.info(f"Resized image from {original_size[0]}x{original_size[1]} to {new_size[0]}x{new_size[1]}")
        else:
            logger.info(f"Image already within limits: {original_size[0]}x{original_size[1]}")

        return image

    except Exception as e:
        logger.error(f"Image resize error: {e}")
        raise ValueError(f"Failed to resize image: {e}")


def compress_image(image: Image.Image, quality: int = JPEG_QUALITY) -> bytes:
    """
    Compress an image to JPEG format

    Args:
        image: PIL Image object
        quality: JPEG quality (1-100, default 85)

    Returns:
        Compressed image as bytes
    """
    try:
        buffer = io.BytesIO()

        # Save as JPEG with optimization
        image.save(
            buffer,
            format='JPEG',
            quality=quality,
            optimize=True,
            progressive=True
        )

        compressed_bytes = buffer.getvalue()

        logger.info(f"Compressed image to {len(compressed_bytes)} bytes (quality={quality})")

        return compressed_bytes

    except Exception as e:
        logger.error(f"Image compression error: {e}")
        raise ValueError(f"Failed to compress image: {e}")


def optimize_image(base64_string: str, max_width: int = MAX_WIDTH, max_height: int = MAX_HEIGHT, quality: int = JPEG_QUALITY) -> Tuple[bytes, dict]:
    """
    Complete pipeline: decode, resize, and compress a base64 image

    Args:
        base64_string: Base64 data URL string
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        quality: JPEG compression quality (1-100)

    Returns:
        Tuple of (compressed_image_bytes, optimization_info_dict)
    """
    try:
        # Decode base64 to PIL Image
        image = decode_base64_image(base64_string)
        original_size = len(base64_string.split(',')[1].encode())
        original_width, original_height = image.size

        # Resize if necessary
        image = resize_image(image, max_width, max_height)
        final_width, final_height = image.size

        # Compress to JPEG
        compressed_bytes = compress_image(image, quality)
        compressed_size = len(compressed_bytes)

        # Calculate compression ratio
        compression_ratio = compressed_size / original_size if original_size > 0 else 0

        optimization_info = {
            'original_size': original_size,
            'optimized_size': compressed_size,
            'compression_ratio': round(compression_ratio, 2),
            'width': final_width,
            'height': final_height,
            'saved_bytes': original_size - compressed_size,
            'saved_percentage': round((1 - compression_ratio) * 100, 1)
        }

        logger.info(f"Optimization complete: {optimization_info['saved_percentage']}% size reduction")

        return compressed_bytes, optimization_info

    except Exception as e:
        logger.error(f"Image optimization error: {e}")
        raise ValueError(f"Failed to optimize image: {e}")


def save_optimized_image(image_bytes: bytes, file_path: str) -> None:
    """
    Save optimized image bytes to a file

    Args:
        image_bytes: Image data as bytes
        file_path: Path where to save the file
    """
    try:
        with open(file_path, 'wb') as f:
            f.write(image_bytes)

        logger.info(f"Saved optimized image to: {file_path}")

    except Exception as e:
        logger.error(f"Error saving image: {e}")
        raise IOError(f"Failed to save image: {e}")


def get_image_info(base64_string: str) -> dict:
    """
    Extract basic information from a base64 image without full optimization

    Args:
        base64_string: Base64 data URL string

    Returns:
        Dictionary with image information
    """
    try:
        image = decode_base64_image(base64_string)

        return {
            'width': image.size[0],
            'height': image.size[1],
            'mode': image.mode,
            'format': image.format,
            'size_bytes': len(base64_string.split(',')[1].encode())
        }

    except Exception as e:
        logger.error(f"Error getting image info: {e}")
        raise ValueError(f"Failed to get image info: {e}")
