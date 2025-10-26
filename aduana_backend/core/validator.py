"""
Validation Rules Module
Implements the 5 business validation rules (R1-R5) for document consistency
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from models.schemas import (
    ValidationError,
    AllExtractedData,
    CapturedData
)

# Configure logging
logger = logging.getLogger(__name__)

# Validation thresholds
DODA_MAX_AGE_DAYS = 3


def normalize_string(text: str) -> str:
    """
    Normalize string for comparison (lowercase, remove extra spaces, accents)

    Args:
        text: String to normalize

    Returns:
        Normalized string
    """
    import unicodedata

    # Remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    # Lowercase and remove extra spaces
    return ' '.join(text.lower().split())


def strings_match(str1: str, str2: str, threshold: float = 0.9) -> bool:
    """
    Check if two strings match with fuzzy matching

    Args:
        str1: First string
        str2: Second string
        threshold: Similarity threshold (0-1)

    Returns:
        True if strings are similar enough
    """
    # Exact match after normalization
    norm1 = normalize_string(str1)
    norm2 = normalize_string(str2)

    if norm1 == norm2:
        return True

    # Check if one contains the other (for cases like "Juan Perez" vs "Juan Perez Garcia")
    if norm1 in norm2 or norm2 in norm1:
        return True

    # Simple similarity: count matching words
    words1 = set(norm1.split())
    words2 = set(norm2.split())

    if not words1 or not words2:
        return False

    intersection = words1 & words2
    union = words1 | words2

    similarity = len(intersection) / len(union)

    return similarity >= threshold


def validate_r1_doda_vigencia(extracted_data: AllExtractedData) -> Optional[ValidationError]:
    """
    R1: Vigencia del DODA
    Verifica que la Fecha de Emisión del DODA no tenga más de 3 días de antigüedad

    Args:
        extracted_data: All extracted data from documents

    Returns:
        ValidationError if validation fails, None if passes
    """
    logger.info("Validating R1: DODA Vigencia")

    try:
        fecha_emision_str = extracted_data.doda.fecha_emision

        # Check for missing data
        if fecha_emision_str == "NO_ENCONTRADO" or not fecha_emision_str:
            return ValidationError(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                message="No se pudo extraer la fecha de emisión del DODA",
                severity="error"
            )

        # Parse date
        try:
            fecha_emision = datetime.strptime(fecha_emision_str, "%Y-%m-%d")
        except ValueError:
            return ValidationError(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                message=f"Formato de fecha inválido en DODA: {fecha_emision_str}",
                severity="error"
            )

        # Calculate age
        hoy = datetime.now()
        edad_dias = (hoy - fecha_emision).days

        logger.info(f"DODA emission date: {fecha_emision_str}, Age: {edad_dias} days")

        # Validate age
        if edad_dias > DODA_MAX_AGE_DAYS:
            return ValidationError(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                message=f"El DODA tiene {edad_dias} días de antigüedad (máximo permitido: {DODA_MAX_AGE_DAYS} días). Fecha de emisión: {fecha_emision_str}",
                severity="error"
            )

        if edad_dias < 0:
            return ValidationError(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                message=f"La fecha de emisión del DODA es futura: {fecha_emision_str}",
                severity="error"
            )

        logger.info("✓ R1 validation passed")
        return None

    except Exception as e:
        logger.error(f"Error in R1 validation: {e}", exc_info=True)
        return ValidationError(
            rule_id="R1",
            rule_name="Vigencia del DODA",
            message=f"Error al validar vigencia del DODA: {str(e)}",
            severity="error"
        )


def validate_r2_placas(extracted_data: AllExtractedData) -> List[ValidationError]:
    """
    R2: Coincidencia de Placas
    Compara las placas del tracto y remolque extraídas del Manifiesto con las placas
    extraídas de las fotos físicas

    Args:
        extracted_data: All extracted data from documents

    Returns:
        List of ValidationErrors (empty if all pass)
    """
    logger.info("Validating R2: Placas Coincidence")

    errors = []

    # Validate tractor plate
    try:
        placa_manifest_tracto = extracted_data.manifest.placa_tracto
        placa_foto_tracto = extracted_data.tractor_plate.plate_number

        logger.info(f"Tractor plate - Manifest: '{placa_manifest_tracto}', Photo: '{placa_foto_tracto}'")

        # Check for missing data
        if placa_manifest_tracto == "NO_ENCONTRADO" or not placa_manifest_tracto:
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Tracto",
                message="No se pudo extraer la placa del tracto del Manifiesto",
                severity="error"
            ))
        elif placa_foto_tracto == "NO_LEGIBLE" or not placa_foto_tracto:
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Tracto",
                message="No se pudo leer la placa del tracto en la foto",
                severity="error"
            ))
        elif not strings_match(placa_manifest_tracto, placa_foto_tracto):
            confidence = extracted_data.tractor_plate.confidence or 0.0
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Tracto",
                message=f"La placa del tracto no coincide. Manifiesto: '{placa_manifest_tracto}', Foto: '{placa_foto_tracto}' (confianza: {confidence:.0%})",
                severity="error"
            ))
        else:
            logger.info("✓ Tractor plate matches")

    except Exception as e:
        logger.error(f"Error validating tractor plate: {e}", exc_info=True)
        errors.append(ValidationError(
            rule_id="R2",
            rule_name="Coincidencia de Placas - Tracto",
            message=f"Error al validar placa del tracto: {str(e)}",
            severity="error"
        ))

    # Validate trailer plate
    try:
        placa_manifest_remolque = extracted_data.manifest.placa_remolque
        placa_foto_remolque = extracted_data.trailer_plate.plate_number

        logger.info(f"Trailer plate - Manifest: '{placa_manifest_remolque}', Photo: '{placa_foto_remolque}'")

        # Check for missing data
        if placa_manifest_remolque == "NO_ENCONTRADO" or not placa_manifest_remolque:
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Remolque",
                message="No se pudo extraer la placa del remolque del Manifiesto",
                severity="error"
            ))
        elif placa_foto_remolque == "NO_LEGIBLE" or not placa_foto_remolque:
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Remolque",
                message="No se pudo leer la placa del remolque en la foto",
                severity="error"
            ))
        elif not strings_match(placa_manifest_remolque, placa_foto_remolque):
            confidence = extracted_data.trailer_plate.confidence or 0.0
            errors.append(ValidationError(
                rule_id="R2",
                rule_name="Coincidencia de Placas - Remolque",
                message=f"La placa del remolque no coincide. Manifiesto: '{placa_manifest_remolque}', Foto: '{placa_foto_remolque}' (confianza: {confidence:.0%})",
                severity="error"
            ))
        else:
            logger.info("✓ Trailer plate matches")

    except Exception as e:
        logger.error(f"Error validating trailer plate: {e}", exc_info=True)
        errors.append(ValidationError(
            rule_id="R2",
            rule_name="Coincidencia de Placas - Remolque",
            message=f"Error al validar placa del remolque: {str(e)}",
            severity="error"
        ))

    if not errors:
        logger.info("✓ R2 validation passed")

    return errors


def validate_r3_cruce_manifest_prefile(extracted_data: AllExtractedData) -> List[ValidationError]:
    """
    R3: Cruce Manifest vs. Entry/Prefile
    Valida que los campos coincidan entre el Manifiesto y el Entry/Prefile:
    - Número de Entry
    - Broker
    - Descripción de la mercancía
    - Cantidad
    - Pesos/Monto

    Args:
        extracted_data: All extracted data from documents

    Returns:
        List of ValidationErrors (empty if all pass)
    """
    logger.info("Validating R3: Manifest vs Prefile Cross-Check")

    errors = []
    manifest = extracted_data.manifest
    prefile = extracted_data.prefile

    # R3.1: Entry Number
    try:
        if manifest.numero_entry == "NO_ENCONTRADO" or prefile.numero_entry == "NO_ENCONTRADO":
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Número Entry",
                message="No se pudo extraer el número de entry de uno o ambos documentos",
                severity="error"
            ))
        elif not strings_match(manifest.numero_entry, prefile.numero_entry):
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Número Entry",
                message=f"El número de entry no coincide. Manifiesto: '{manifest.numero_entry}', Prefile: '{prefile.numero_entry}'",
                severity="error"
            ))
        else:
            logger.info(f"✓ Entry number matches: {manifest.numero_entry}")
    except Exception as e:
        logger.error(f"Error validating entry number: {e}")
        errors.append(ValidationError(
            rule_id="R3",
            rule_name="Cruce Manifest/Prefile - Número Entry",
            message=f"Error al validar número de entry: {str(e)}",
            severity="error"
        ))

    # R3.2: Broker (primeros 3 dígitos del Entry Number)
    try:
        # Extract broker from Entry Number (first 3 digits)
        # Entry format examples: "600258901", "231-2712401-9"
        def extract_broker_from_entry(entry: str) -> str:
            """Extract first 3 digits from Entry Number as Broker code"""
            if entry == "NO_ENCONTRADO" or not entry:
                return "NO_ENCONTRADO"
            # Remove all non-numeric characters
            digits = ''.join(c for c in entry if c.isdigit())
            # Return first 3 digits
            if len(digits) >= 3:
                return digits[:3]
            return "NO_ENCONTRADO"

        broker_manifest = extract_broker_from_entry(manifest.numero_entry)
        broker_prefile = extract_broker_from_entry(prefile.numero_entry)

        logger.info(f"Broker codes - Manifest: '{broker_manifest}' (from {manifest.numero_entry}), Prefile: '{broker_prefile}' (from {prefile.numero_entry})")

        if broker_manifest == "NO_ENCONTRADO" or broker_prefile == "NO_ENCONTRADO":
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Broker",
                message="No se pudo extraer el código de broker del número de entry de uno o ambos documentos",
                severity="error"
            ))
        elif broker_manifest != broker_prefile:
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Broker",
                message=f"El código de broker no coincide. Manifiesto: '{broker_manifest}' (Entry: {manifest.numero_entry}), Prefile: '{broker_prefile}' (Entry: {prefile.numero_entry})",
                severity="error"
            ))
        else:
            logger.info(f"✓ Broker code matches: {broker_manifest}")
    except Exception as e:
        logger.error(f"Error validating broker: {e}")
        errors.append(ValidationError(
            rule_id="R3",
            rule_name="Cruce Manifest/Prefile - Broker",
            message=f"Error al validar broker: {str(e)}",
            severity="error"
        ))

    # R3.3: Merchandise Description
    try:
        if manifest.descripcion_mercancia == "NO_ENCONTRADO" or prefile.descripcion_mercancia == "NO_ENCONTRADO":
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Descripción",
                message="No se pudo extraer la descripción de mercancía de uno o ambos documentos",
                severity="error"
            ))
        elif not strings_match(manifest.descripcion_mercancia, prefile.descripcion_mercancia, threshold=0.7):
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Descripción",
                message=f"La descripción de mercancía no coincide. Manifiesto: '{manifest.descripcion_mercancia}', Prefile: '{prefile.descripcion_mercancia}'",
                severity="warning"  # Warning because descriptions might vary
            ))
        else:
            logger.info(f"✓ Merchandise description matches")
    except Exception as e:
        logger.error(f"Error validating merchandise description: {e}")
        errors.append(ValidationError(
            rule_id="R3",
            rule_name="Cruce Manifest/Prefile - Descripción",
            message=f"Error al validar descripción de mercancía: {str(e)}",
            severity="error"
        ))

    # R3.4: Quantity
    try:
        if manifest.cantidad == 0 or prefile.cantidad == 0:
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Cantidad",
                message="No se pudo extraer la cantidad de uno o ambos documentos",
                severity="error"
            ))
        elif abs(manifest.cantidad - prefile.cantidad) > 0.01:  # Small tolerance for floating point
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Cantidad",
                message=f"La cantidad no coincide. Manifiesto: {manifest.cantidad}, Prefile: {prefile.cantidad}",
                severity="error"
            ))
        else:
            logger.info(f"✓ Quantity matches: {manifest.cantidad}")
    except Exception as e:
        logger.error(f"Error validating quantity: {e}")
        errors.append(ValidationError(
            rule_id="R3",
            rule_name="Cruce Manifest/Prefile - Cantidad",
            message=f"Error al validar cantidad: {str(e)}",
            severity="error"
        ))

    # R3.5: Weight/Amount
    try:
        if manifest.peso_monto == 0 or prefile.peso_monto == 0:
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Peso/Monto",
                message="No se pudo extraer el peso/monto de uno o ambos documentos",
                severity="error"
            ))
        elif abs(manifest.peso_monto - prefile.peso_monto) > 0.01:
            errors.append(ValidationError(
                rule_id="R3",
                rule_name="Cruce Manifest/Prefile - Peso/Monto",
                message=f"El peso/monto no coincide. Manifiesto: {manifest.peso_monto}, Prefile: {prefile.peso_monto}",
                severity="error"
            ))
        else:
            logger.info(f"✓ Weight/Amount matches: {manifest.peso_monto}")
    except Exception as e:
        logger.error(f"Error validating weight/amount: {e}")
        errors.append(ValidationError(
            rule_id="R3",
            rule_name="Cruce Manifest/Prefile - Peso/Monto",
            message=f"Error al validar peso/monto: {str(e)}",
            severity="error"
        ))

    if not errors:
        logger.info("✓ R3 validation passed")

    return errors


def validate_r4_aduana(extracted_data: AllExtractedData) -> Optional[ValidationError]:
    """
    R4: Coincidencia de Aduana
    Compara la Sección Aduanera del DODA con la Aduana de Arribo del Manifiesto

    Args:
        extracted_data: All extracted data from documents

    Returns:
        ValidationError if validation fails, None if passes
    """
    logger.info("Validating R4: Customs Coincidence")

    try:
        seccion_aduanera = extracted_data.doda.seccion_aduanera
        aduana_arribo = extracted_data.manifest.aduana_arribo

        logger.info(f"Customs - DODA: '{seccion_aduanera}', Manifest: '{aduana_arribo}'")

        # Check for missing data
        if seccion_aduanera == "NO_ENCONTRADO" or not seccion_aduanera:
            return ValidationError(
                rule_id="R4",
                rule_name="Coincidencia de Aduana",
                message="No se pudo extraer la sección aduanera del DODA",
                severity="error"
            )

        if aduana_arribo == "NO_ENCONTRADO" or not aduana_arribo:
            return ValidationError(
                rule_id="R4",
                rule_name="Coincidencia de Aduana",
                message="No se pudo extraer la aduana de arribo del Manifiesto",
                severity="error"
            )

        # Validate match
        if not strings_match(seccion_aduanera, aduana_arribo):
            return ValidationError(
                rule_id="R4",
                rule_name="Coincidencia de Aduana",
                message=f"La aduana no coincide. DODA: '{seccion_aduanera}', Manifiesto: '{aduana_arribo}'",
                severity="error"
            )

        logger.info("✓ R4 validation passed")
        return None

    except Exception as e:
        logger.error(f"Error in R4 validation: {e}", exc_info=True)
        return ValidationError(
            rule_id="R4",
            rule_name="Coincidencia de Aduana",
            message=f"Error al validar coincidencia de aduana: {str(e)}",
            severity="error"
        )


def validate_r5_operador(extracted_data: AllExtractedData, driver_name: str) -> Optional[ValidationError]:
    """
    R5: Coincidencia de Operador
    Compara el Nombre del Operador extraído del Manifiesto con el nombre ingresado
    manualmente por el usuario

    Args:
        extracted_data: All extracted data from documents
        driver_name: Driver name entered by user in the form

    Returns:
        ValidationError if validation fails, None if passes
    """
    logger.info("Validating R5: Driver Name Coincidence")

    try:
        nombre_manifest = extracted_data.manifest.nombre_operador
        nombre_usuario = driver_name

        logger.info(f"Driver name - Manifest: '{nombre_manifest}', User input: '{nombre_usuario}'")

        # Check for missing data
        if nombre_manifest == "NO_ENCONTRADO" or not nombre_manifest:
            return ValidationError(
                rule_id="R5",
                rule_name="Coincidencia de Operador",
                message="No se pudo extraer el nombre del operador del Manifiesto",
                severity="error"
            )

        if not nombre_usuario or not nombre_usuario.strip():
            return ValidationError(
                rule_id="R5",
                rule_name="Coincidencia de Operador",
                message="No se ingresó el nombre del operador en el formulario",
                severity="error"
            )

        # Validate match (more lenient threshold for names)
        if not strings_match(nombre_manifest, nombre_usuario, threshold=0.7):
            return ValidationError(
                rule_id="R5",
                rule_name="Coincidencia de Operador",
                message=f"El nombre del operador no coincide. Manifiesto: '{nombre_manifest}', Formulario: '{nombre_usuario}'",
                severity="error"
            )

        logger.info("✓ R5 validation passed")
        return None

    except Exception as e:
        logger.error(f"Error in R5 validation: {e}", exc_info=True)
        return ValidationError(
            rule_id="R5",
            rule_name="Coincidencia de Operador",
            message=f"Error al validar coincidencia de operador: {str(e)}",
            severity="error"
        )


def validate_all_rules(
    extracted_data: AllExtractedData,
    original_data: CapturedData
) -> List[ValidationError]:
    """
    Execute all validation rules (R1-R5) and collect errors

    Args:
        extracted_data: Data extracted from documents by AI
        original_data: Original data submitted by user

    Returns:
        List of all validation errors (empty if all validations pass)
    """
    logger.info("=" * 70)
    logger.info("STARTING VALIDATION - EXECUTING ALL 5 RULES")
    logger.info("=" * 70)

    all_errors = []

    # R1: DODA Vigencia
    error_r1 = validate_r1_doda_vigencia(extracted_data)
    if error_r1:
        all_errors.append(error_r1)

    # R2: Placas
    errors_r2 = validate_r2_placas(extracted_data)
    all_errors.extend(errors_r2)

    # R3: Cruce Manifest/Prefile
    errors_r3 = validate_r3_cruce_manifest_prefile(extracted_data)
    all_errors.extend(errors_r3)

    # R4: Aduana
    error_r4 = validate_r4_aduana(extracted_data)
    if error_r4:
        all_errors.append(error_r4)

    # R5: Operador
    error_r5 = validate_r5_operador(extracted_data, original_data.driverData.name)
    if error_r5:
        all_errors.append(error_r5)

    # Summary
    logger.info("=" * 70)
    if all_errors:
        logger.warning(f"VALIDATION COMPLETED - {len(all_errors)} ERROR(S) FOUND")
        for error in all_errors:
            logger.warning(f"  [{error.rule_id}] {error.message}")
    else:
        logger.info("VALIDATION COMPLETED - ALL RULES PASSED ✓")
    logger.info("=" * 70)

    return all_errors
