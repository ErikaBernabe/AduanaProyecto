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


# ============================================================================
# Enhanced Validation Response Models (Modal UI Support)
# ============================================================================

class FieldExtractionStatus(BaseModel):
    """Estado de extracción de un campo individual"""
    field_name: str = Field(..., description="Nombre técnico del campo")
    field_label: str = Field(..., description="Etiqueta legible del campo")
    value: str | float | int = Field(..., description="Valor extraído")
    status: str = Field(..., description="success | not_found | low_confidence")
    icon: str = Field(..., description="✅ | ❌ | ⚠️")
    confidence: Optional[float] = Field(None, description="Nivel de confianza 0-1")

    class Config:
        json_schema_extra = {
            "example": {
                "field_name": "descripcion_mercancia",
                "field_label": "Descripción de Mercancía",
                "value": "Steel coils, hot rolled",
                "status": "success",
                "icon": "✅",
                "confidence": 0.95
            }
        }


class DocumentExtractionReport(BaseModel):
    """Reporte detallado de extracción de un documento"""
    document_type: str = Field(..., description="DODA | E-Manifest | Prefile | Placa")
    document_name: str = Field(..., description="Nombre legible del documento")
    total_fields: int = Field(..., description="Total de campos esperados")
    extracted_fields: int = Field(..., description="Campos extraídos exitosamente")
    not_found_fields: int = Field(..., description="Campos no encontrados")
    confidence_score: float = Field(..., description="Confianza promedio 0-1")
    fields: list[FieldExtractionStatus] = Field(..., description="Detalle de cada campo")

    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "manifest",
                "document_name": "E-Manifest (Manifiesto Electrónico)",
                "total_fields": 9,
                "extracted_fields": 7,
                "not_found_fields": 2,
                "confidence_score": 0.78,
                "fields": []
            }
        }


class ComparisonDetail(BaseModel):
    """Detalle de comparación entre dos valores"""
    label: str = Field(..., description="Etiqueta del campo")
    value1: str = Field(..., description="Valor del primer documento")
    value2: str = Field(..., description="Valor del segundo documento")
    source1: str = Field(..., description="Fuente del primer valor")
    source2: str = Field(..., description="Fuente del segundo valor")
    matches: bool = Field(..., description="Si los valores coinciden")
    similarity: Optional[float] = Field(None, description="Similitud 0-1 si aplica")
    icon: str = Field(..., description="✅ | ❌ | ⚠️")


class RuleValidationDetail(BaseModel):
    """Detalle completo de validación de una regla"""
    rule_id: str = Field(..., description="R1, R2, R3, R4, R5")
    rule_name: str = Field(..., description="Nombre de la regla")
    rule_description: str = Field(..., description="Descripción breve")
    status: str = Field(..., description="passed | failed | warning | not_applicable")
    icon: str = Field(..., description="✅ | ❌ | ⚠️ | ➖")
    summary: str = Field(..., description="Resumen del resultado")
    details: list[str] = Field(default_factory=list, description="Detalles adicionales")
    comparisons: list[ComparisonDetail] = Field(default_factory=list, description="Comparaciones realizadas")
    errors: list[ValidationError] = Field(default_factory=list, description="Errores específicos")
    recommendation: Optional[str] = Field(None, description="Recomendación de acción")

    class Config:
        json_schema_extra = {
            "example": {
                "rule_id": "R5",
                "rule_name": "Coincidencia de Operador",
                "rule_description": "Verifica que el operador del formulario coincida con el del manifiesto",
                "status": "passed",
                "icon": "✅",
                "summary": "El operador coincide con el manifiesto",
                "details": ["Formulario: Andy Anderson", "Manifest: Andy Anderson", "Similitud: 100%"],
                "comparisons": [],
                "errors": [],
                "recommendation": None
            }
        }


class ValidationSummary(BaseModel):
    """Resumen general de validación"""
    total_rules: int = Field(default=5, description="Total de reglas validadas")
    passed_rules: int = Field(..., description="Reglas que pasaron")
    failed_rules: int = Field(..., description="Reglas que fallaron")
    warning_rules: int = Field(..., description="Reglas con advertencias")
    overall_status: str = Field(..., description="success | partial | failed")
    confidence_average: float = Field(..., description="Confianza promedio de extracción 0-1")
    processing_time: float = Field(..., description="Tiempo de procesamiento en segundos")

    class Config:
        json_schema_extra = {
            "example": {
                "total_rules": 5,
                "passed_rules": 2,
                "failed_rules": 3,
                "warning_rules": 0,
                "overall_status": "partial",
                "confidence_average": 0.72,
                "processing_time": 3.2
            }
        }


class EnhancedValidationResponse(BaseModel):
    """Respuesta expandida con toda la información para el modal"""
    success: bool = Field(..., description="True si todas las validaciones pasaron")
    message: str = Field(..., description="Mensaje resumen")
    errors: list[ValidationError] = Field(default_factory=list, description="Lista de errores (compatibilidad)")

    # Datos expandidos para el modal
    summary: ValidationSummary = Field(..., description="Resumen general")
    rules: list[RuleValidationDetail] = Field(..., description="Detalle de cada regla R1-R5")
    extraction: list[DocumentExtractionReport] = Field(..., description="Reporte de extracción por documento")
    timestamp: str = Field(..., description="Timestamp ISO 8601")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Se encontraron 3 errores de validación",
                "errors": [],
                "summary": {
                    "total_rules": 5,
                    "passed_rules": 2,
                    "failed_rules": 3,
                    "warning_rules": 0,
                    "overall_status": "partial",
                    "confidence_average": 0.72,
                    "processing_time": 3.2
                },
                "rules": [],
                "extraction": [],
                "timestamp": "2025-10-26T14:32:15.123Z"
            }
        }
