"""
Pydantic schemas for request/response validation
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field, validator
import re


class DriverData(BaseModel):
    """
    Driver information captured from the frontend
    """
    name: str = Field(..., description="Driver's full name")
    tractorPlate: str = Field(..., description="Base64 encoded image of tractor plate")
    trailerPlate: str = Field(..., description="Base64 encoded image of trailer plate")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Driver name cannot be empty')
        return v.strip()

    @validator('tractorPlate', 'trailerPlate')
    def validate_base64_image(cls, v):
        if not v:
            raise ValueError('Image data cannot be empty')
        # Check if it's a valid base64 image string
        if not v.startswith('data:image/'):
            raise ValueError('Invalid image format. Must be a base64 data URL')
        return v


class Documents(BaseModel):
    """
    Document images captured from the frontend
    """
    doda: str = Field(..., description="Base64 encoded DODA document image")
    emanifest: str = Field(..., description="Base64 encoded E-Manifest document image")
    prefile: str = Field(..., description="Base64 encoded Prefile document image")

    @validator('doda', 'emanifest', 'prefile')
    def validate_base64_image(cls, v):
        if not v:
            raise ValueError('Document image cannot be empty')
        if not v.startswith('data:image/'):
            raise ValueError('Invalid image format. Must be a base64 data URL')
        return v


class CapturedData(BaseModel):
    """
    Complete data structure sent from the React frontend
    Matches the structure in InspectionScreen.js
    """
    driverData: DriverData = Field(..., description="Driver information and plate photos")
    documents: Documents = Field(..., description="All required document images")

    class Config:
        json_schema_extra = {
            "example": {
                "driverData": {
                    "name": "Juan Pérez",
                    "tractorPlate": "data:image/png;base64,iVBORw0KG...",
                    "trailerPlate": "data:image/png;base64,iVBORw0KG..."
                },
                "documents": {
                    "doda": "data:image/jpeg;base64,/9j/4AAQ...",
                    "emanifest": "data:image/jpeg;base64,/9j/4AAQ...",
                    "prefile": "data:image/jpeg;base64,/9j/4AAQ..."
                }
            }
        }


class ValidationError(BaseModel):
    """
    Individual validation error for a specific rule
    """
    rule_id: str = Field(..., description="Rule identifier (R1, R2, R3, R4, R5)")
    rule_name: str = Field(..., description="Human-readable rule name")
    message: str = Field(..., description="Error message describing the issue")
    severity: str = Field(..., description="Error severity: 'error' or 'warning'")

    @validator('rule_id')
    def validate_rule_id(cls, v):
        valid_rules = ['R1', 'R2', 'R3', 'R4', 'R5']
        if v not in valid_rules:
            raise ValueError(f'Invalid rule_id. Must be one of: {valid_rules}')
        return v

    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['error', 'warning']
        if v not in valid_severities:
            raise ValueError(f'Invalid severity. Must be one of: {valid_severities}')
        return v


class ValidationResponse(BaseModel):
    """
    Response structure for the validation endpoint
    """
    success: bool = Field(..., description="True if all validations passed")
    message: str = Field(..., description="Summary message")
    errors: list[ValidationError] = Field(default_factory=list, description="List of validation errors")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Se encontraron 2 errores de validación",
                "errors": [
                    {
                        "rule_id": "R1",
                        "rule_name": "Vigencia del DODA",
                        "message": "El DODA tiene más de 3 días de antigüedad",
                        "severity": "error"
                    }
                ]
            }
        }


class ImageOptimizationResult(BaseModel):
    """
    Internal model for tracking optimized images
    """
    original_size: int = Field(..., description="Original image size in bytes")
    optimized_size: int = Field(..., description="Optimized image size in bytes")
    compression_ratio: float = Field(..., description="Compression ratio (0-1)")
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")


# ============================================================================
# AI-Extracted Data Models (Phase 3)
# ============================================================================

class ExtractedDODAData(BaseModel):
    """
    Data extracted from DODA document via OCR/AI
    """
    fecha_emision: str = Field(..., description="Emission date in YYYY-MM-DD format")
    seccion_aduanera: str = Field(..., description="Customs section")

    class Config:
        json_schema_extra = {
            "example": {
                "fecha_emision": "2025-10-20",
                "seccion_aduanera": "Tijuana"
            }
        }


class ExtractedManifestData(BaseModel):
    """
    Data extracted from E-Manifest document via OCR/AI
    """
    placa_tracto: str = Field(..., description="Tractor plate number")
    placa_remolque: str = Field(..., description="Trailer plate number")
    nombre_operador: str = Field(..., description="Driver/operator name")
    aduana_arribo: str = Field(..., description="Arrival customs")
    numero_entry: str = Field(..., description="Entry number")
    broker: str = Field(..., description="Broker name")
    descripcion_mercancia: str = Field(..., description="Merchandise description")
    cantidad: float = Field(..., description="Quantity")
    peso_monto: float = Field(..., description="Weight or amount")

    class Config:
        json_schema_extra = {
            "example": {
                "placa_tracto": "ABC-123",
                "placa_remolque": "XYZ-789",
                "nombre_operador": "Juan Pérez García",
                "aduana_arribo": "Tijuana",
                "numero_entry": "ENT-2025-001234",
                "broker": "Brokers Unidos S.A.",
                "descripcion_mercancia": "Productos electrónicos",
                "cantidad": 100,
                "peso_monto": 5000.50
            }
        }


class ExtractedPrefileData(BaseModel):
    """
    Data extracted from Prefile document via OCR/AI
    """
    numero_entry: str = Field(..., description="Entry number")
    broker: str = Field(..., description="Broker name")
    descripcion_mercancia: str = Field(..., description="Merchandise description")
    cantidad: float = Field(..., description="Quantity")
    peso_monto: float = Field(..., description="Weight or amount")

    class Config:
        json_schema_extra = {
            "example": {
                "numero_entry": "ENT-2025-001234",
                "broker": "Brokers Unidos S.A.",
                "descripcion_mercancia": "Productos electrónicos",
                "cantidad": 100,
                "peso_monto": 5000.50
            }
        }


class ExtractedPlateData(BaseModel):
    """
    Data extracted from plate photo via OCR/AI
    """
    plate_number: str = Field(..., description="License plate number")
    confidence: Optional[float] = Field(None, description="OCR confidence level (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "plate_number": "ABC-123",
                "confidence": 0.95
            }
        }


class AllExtractedData(BaseModel):
    """
    Complete extracted data from all documents
    """
    doda: ExtractedDODAData
    manifest: ExtractedManifestData
    prefile: ExtractedPrefileData
    tractor_plate: ExtractedPlateData
    trailer_plate: ExtractedPlateData

    class Config:
        json_schema_extra = {
            "example": {
                "doda": {
                    "fecha_emision": "2025-10-20",
                    "seccion_aduanera": "Tijuana"
                },
                "manifest": {
                    "placa_tracto": "ABC-123",
                    "placa_remolque": "XYZ-789",
                    "nombre_operador": "Juan Pérez García",
                    "aduana_arribo": "Tijuana",
                    "numero_entry": "ENT-2025-001234",
                    "broker": "Brokers Unidos S.A.",
                    "descripcion_mercancia": "Productos electrónicos",
                    "cantidad": 100,
                    "peso_monto": 5000.50
                },
                "prefile": {
                    "numero_entry": "ENT-2025-001234",
                    "broker": "Brokers Unidos S.A.",
                    "descripcion_mercancia": "Productos electrónicos",
                    "cantidad": 100,
                    "peso_monto": 5000.50
                },
                "tractor_plate": {
                    "plate_number": "ABC-123",
                    "confidence": 0.95
                },
                "trailer_plate": {
                    "plate_number": "XYZ-789",
                    "confidence": 0.93
                }
            }
        }
