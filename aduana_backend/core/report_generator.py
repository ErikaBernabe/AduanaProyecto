"""
Report Generator Module
Generates detailed extraction and validation reports for the modal UI
"""

import logging
from typing import List
from datetime import datetime

from models.schemas import (
    FieldExtractionStatus,
    DocumentExtractionReport,
    AllExtractedData,
    ExtractedDODAData,
    ExtractedManifestData,
    ExtractedPrefileData,
    ExtractedPlateData
)

logger = logging.getLogger(__name__)


def generate_field_status(
    field_name: str,
    field_label: str,
    value: any,
    confidence: float = None
) -> FieldExtractionStatus:
    """
    Genera el estado de extracción de un campo individual

    Args:
        field_name: Nombre técnico del campo
        field_label: Etiqueta legible
        value: Valor extraído
        confidence: Confianza opcional

    Returns:
        FieldExtractionStatus
    """
    # Determinar status basado en el valor
    if isinstance(value, str):
        if value == "NO_ENCONTRADO" or value == "NO_LEGIBLE":
            status = "not_found"
            icon = "❌"
        else:
            status = "success"
            icon = "✅"
    elif isinstance(value, (int, float)):
        if value == 0 or value == 0.0:
            # Verificar si es un campo que debería tener valor > 0
            if field_name in ["cantidad", "peso_monto"]:
                status = "not_found"
                icon = "❌"
            else:
                status = "success"
                icon = "✅"
        else:
            status = "success"
            icon = "✅"
    else:
        status = "success"
        icon = "✅"

    # Advertencia si confidence es baja
    if confidence and confidence < 0.7:
        status = "low_confidence"
        icon = "⚠️"

    return FieldExtractionStatus(
        field_name=field_name,
        field_label=field_label,
        value=str(value),
        status=status,
        icon=icon,
        confidence=confidence
    )


def generate_doda_report(doda: ExtractedDODAData) -> DocumentExtractionReport:
    """Genera reporte de extracción del DODA"""

    fields = [
        generate_field_status(
            "fecha_emision",
            "Fecha de Emisión",
            doda.fecha_emision
        ),
        generate_field_status(
            "seccion_aduanera",
            "Sección Aduanera",
            doda.seccion_aduanera
        )
    ]

    extracted = sum(1 for f in fields if f.status == "success")
    not_found = sum(1 for f in fields if f.status == "not_found")
    total = len(fields)

    confidence_score = extracted / total if total > 0 else 0.0

    return DocumentExtractionReport(
        document_type="DODA",
        document_name="DODA (Declaración de Operación)",
        total_fields=total,
        extracted_fields=extracted,
        not_found_fields=not_found,
        confidence_score=confidence_score,
        fields=fields
    )


def generate_manifest_report(manifest: ExtractedManifestData) -> DocumentExtractionReport:
    """Genera reporte de extracción del E-Manifest"""

    fields = [
        generate_field_status("placa_tracto", "Placa Tracto", manifest.placa_tracto),
        generate_field_status("placa_remolque", "Placa Remolque", manifest.placa_remolque),
        generate_field_status("nombre_operador", "Nombre Operador", manifest.nombre_operador),
        generate_field_status("aduana_arribo", "Aduana de Arribo", manifest.aduana_arribo),
        generate_field_status("numero_entry", "Número de Entry", manifest.numero_entry),
        generate_field_status("broker", "Broker", manifest.broker),
        generate_field_status("descripcion_mercancia", "Descripción Mercancía", manifest.descripcion_mercancia),
        generate_field_status("cantidad", "Cantidad", manifest.cantidad),
        generate_field_status("peso_monto", "Peso/Monto", manifest.peso_monto),
    ]

    extracted = sum(1 for f in fields if f.status == "success")
    not_found = sum(1 for f in fields if f.status == "not_found")
    total = len(fields)

    confidence_score = extracted / total if total > 0 else 0.0

    return DocumentExtractionReport(
        document_type="E-Manifest",
        document_name="E-Manifest (Manifiesto Electrónico)",
        total_fields=total,
        extracted_fields=extracted,
        not_found_fields=not_found,
        confidence_score=confidence_score,
        fields=fields
    )


def generate_prefile_report(prefile: ExtractedPrefileData) -> DocumentExtractionReport:
    """Genera reporte de extracción del Prefile"""

    fields = [
        generate_field_status("numero_entry", "Número de Entry", prefile.numero_entry),
        generate_field_status("broker", "Broker", prefile.broker),
        generate_field_status("descripcion_mercancia", "Descripción Mercancía", prefile.descripcion_mercancia),
        generate_field_status("cantidad", "Cantidad", prefile.cantidad),
        generate_field_status("peso_monto", "Peso/Monto", prefile.peso_monto),
    ]

    extracted = sum(1 for f in fields if f.status == "success")
    not_found = sum(1 for f in fields if f.status == "not_found")
    total = len(fields)

    confidence_score = extracted / total if total > 0 else 0.0

    return DocumentExtractionReport(
        document_type="Prefile",
        document_name="Prefile (Pre-declaración)",
        total_fields=total,
        extracted_fields=extracted,
        not_found_fields=not_found,
        confidence_score=confidence_score,
        fields=fields
    )


def generate_plate_report(
    plate: ExtractedPlateData,
    plate_type: str
) -> DocumentExtractionReport:
    """Genera reporte de extracción de placa"""

    fields = [
        generate_field_status(
            "plate_number",
            "Número de Placa",
            plate.plate_number,
            confidence=plate.confidence
        )
    ]

    extracted = sum(1 for f in fields if f.status == "success")
    not_found = sum(1 for f in fields if f.status == "not_found")
    total = len(fields)

    confidence_score = plate.confidence if plate.confidence else 0.0

    return DocumentExtractionReport(
        document_type=f"Placa_{plate_type}",
        document_name=f"Placa de {plate_type.capitalize()}",
        total_fields=total,
        extracted_fields=extracted,
        not_found_fields=not_found,
        confidence_score=confidence_score,
        fields=fields
    )


def generate_all_extraction_reports(
    extracted_data: AllExtractedData
) -> List[DocumentExtractionReport]:
    """
    Genera todos los reportes de extracción

    Args:
        extracted_data: Todos los datos extraídos

    Returns:
        Lista de DocumentExtractionReport
    """
    logger.info("Generando reportes de extracción para modal...")

    reports = [
        generate_doda_report(extracted_data.doda),
        generate_manifest_report(extracted_data.manifest),
        generate_prefile_report(extracted_data.prefile),
        generate_plate_report(extracted_data.tractor_plate, "tracto"),
        generate_plate_report(extracted_data.trailer_plate, "remolque")
    ]

    logger.info(f"✓ Generados {len(reports)} reportes de extracción")

    return reports


def calculate_overall_confidence(
    extraction_reports: List[DocumentExtractionReport]
) -> float:
    """
    Calcula la confianza promedio de todos los reportes

    Args:
        extraction_reports: Lista de reportes

    Returns:
        Confianza promedio 0-1
    """
    if not extraction_reports:
        return 0.0

    total_confidence = sum(r.confidence_score for r in extraction_reports)
    return total_confidence / len(extraction_reports)
