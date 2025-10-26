"""
Enhanced Validator Module
Wraps existing validator functions to generate detailed RuleValidationDetail responses
"""

import logging
from datetime import datetime
from typing import List

from models.schemas import (
    ValidationError,
    RuleValidationDetail,
    ComparisonDetail,
    AllExtractedData,
    CapturedData
)
from core.validator import (
    validate_r1_doda_vigencia,
    validate_r2_placas,
    validate_r3_cruce_manifest_prefile,
    validate_r4_aduana,
    validate_r5_operador,
    DODA_MAX_AGE_DAYS
)

logger = logging.getLogger(__name__)


def enhance_r1_validation(
    extracted_data: AllExtractedData
) -> RuleValidationDetail:
    """
    R1: Vigencia del DODA con detalle completo
    """
    logger.info("Generating enhanced R1 validation report...")

    error = validate_r1_doda_vigencia(extracted_data)
    fecha_emision = extracted_data.doda.fecha_emision

    if error:
        # Validación falló
        try:
            fecha = datetime.fromisoformat(fecha_emision)
            dias = (datetime.now() - fecha).days

            return RuleValidationDetail(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                rule_description=f"Verifica que el DODA no tenga más de {DODA_MAX_AGE_DAYS} días de antigüedad",
                status="failed",
                icon="❌",
                summary=f"El DODA está vencido ({dias} días de antigüedad)",
                details=[
                    f"📅 Fecha de emisión: {fecha.strftime('%d de %B de %Y')}",
                    f"📆 Fecha actual: {datetime.now().strftime('%d de %B de %Y')}",
                    f"⏳ Días transcurridos: {dias} días",
                    f"⚠️ Límite permitido: {DODA_MAX_AGE_DAYS} días",
                    f"❌ Excede por: {dias - DODA_MAX_AGE_DAYS} días"
                ],
                comparisons=[],
                errors=[error],
                recommendation="Solicitar DODA actualizado antes de cruzar"
            )
        except:
            return RuleValidationDetail(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                rule_description=f"Verifica que el DODA no tenga más de {DODA_MAX_AGE_DAYS} días de antigüedad",
                status="failed",
                icon="❌",
                summary="No se pudo validar la fecha del DODA",
                details=[f"Fecha de emisión: {fecha_emision}"],
                comparisons=[],
                errors=[error],
                recommendation="Verificar manualmente la fecha del DODA"
            )
    else:
        # Validación pasó
        try:
            fecha = datetime.fromisoformat(fecha_emision)
            dias = (datetime.now() - fecha).days

            return RuleValidationDetail(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                rule_description=f"Verifica que el DODA no tenga más de {DODA_MAX_AGE_DAYS} días de antigüedad",
                status="passed",
                icon="✅",
                summary=f"DODA vigente ({dias} días de antigüedad)",
                details=[
                    f"📅 Fecha de emisión: {fecha.strftime('%d de %B de %Y')}",
                    f"⏳ Días transcurridos: {dias} días",
                    f"✅ Límite permitido: {DODA_MAX_AGE_DAYS} días",
                    f"✓ DODA dentro de vigencia"
                ],
                comparisons=[],
                errors=[],
                recommendation=None
            )
        except:
            return RuleValidationDetail(
                rule_id="R1",
                rule_name="Vigencia del DODA",
                rule_description=f"Verifica que el DODA no tenga más de {DODA_MAX_AGE_DAYS} días de antigüedad",
                status="passed",
                icon="✅",
                summary="DODA vigente",
                details=[f"Fecha de emisión: {fecha_emision}"],
                comparisons=[],
                errors=[],
                recommendation=None
            )


def enhance_r2_validation(
    extracted_data: AllExtractedData
) -> RuleValidationDetail:
    """
    R2: Coincidencia de Placas con detalle completo
    """
    logger.info("Generating enhanced R2 validation report...")

    errors = validate_r2_placas(extracted_data)

    placa_tracto_foto = extracted_data.tractor_plate.plate_number
    placa_tracto_manifest = extracted_data.manifest.placa_tracto
    placa_remolque_foto = extracted_data.trailer_plate.plate_number
    placa_remolque_manifest = extracted_data.manifest.placa_remolque

    tracto_matches = placa_tracto_foto.upper() == placa_tracto_manifest.upper()
    remolque_matches = placa_remolque_foto.upper() == placa_remolque_manifest.upper()

    comparisons = [
        ComparisonDetail(
            label="Placa Tracto",
            value1=placa_tracto_foto,
            value2=placa_tracto_manifest,
            source1="Foto",
            source2="Manifest",
            matches=tracto_matches,
            similarity=1.0 if tracto_matches else 0.0,
            icon="✅" if tracto_matches else "❌"
        ),
        ComparisonDetail(
            label="Placa Remolque",
            value1=placa_remolque_foto,
            value2=placa_remolque_manifest,
            source1="Foto",
            source2="Manifest",
            matches=remolque_matches,
            similarity=1.0 if remolque_matches else 0.0,
            icon="✅" if remolque_matches else "❌"
        )
    ]

    if errors:
        return RuleValidationDetail(
            rule_id="R2",
            rule_name="Coincidencia de Placas",
            rule_description="Verifica que las placas fotografiadas coincidan con las del manifiesto",
            status="failed",
            icon="❌",
            summary="Las placas no coinciden con el manifiesto",
            details=[
                f"🚛 Tracto: Foto '{placa_tracto_foto}' {'✅' if tracto_matches else '❌ ≠'} Manifest '{placa_tracto_manifest}'",
                f"🚚 Remolque: Foto '{placa_remolque_foto}' {'✅' if remolque_matches else '❌ ≠'} Manifest '{placa_remolque_manifest}'"
            ],
            comparisons=comparisons,
            errors=errors,
            recommendation="Verificar las placas físicas del vehículo"
        )
    else:
        return RuleValidationDetail(
            rule_id="R2",
            rule_name="Coincidencia de Placas",
            rule_description="Verifica que las placas fotografiadas coincidan con las del manifiesto",
            status="passed",
            icon="✅",
            summary="Las placas coinciden con el manifiesto",
            details=[
                f"🚛 Tracto: Foto '{placa_tracto_foto}' = Manifest '{placa_tracto_manifest}' ✅",
                f"🚚 Remolque: Foto '{placa_remolque_foto}' = Manifest '{placa_remolque_manifest}' ✅"
            ],
            comparisons=comparisons,
            errors=[],
            recommendation=None
        )


def enhance_r3_validation(
    extracted_data: AllExtractedData
) -> RuleValidationDetail:
    """
    R3: Cruce Manifest/Prefile con detalle completo
    """
    logger.info("Generating enhanced R3 validation report...")

    errors = validate_r3_cruce_manifest_prefile(extracted_data)

    manifest = extracted_data.manifest
    prefile = extracted_data.prefile

    # Crear comparaciones
    comparisons = []
    details = []

    # Entry Number
    entry_matches = manifest.numero_entry == prefile.numero_entry
    comparisons.append(ComparisonDetail(
        label="Entry Number",
        value1=manifest.numero_entry,
        value2=prefile.numero_entry,
        source1="Manifest",
        source2="Prefile",
        matches=entry_matches,
        icon="✅" if entry_matches else "❌"
    ))
    details.append(f"{'✅' if entry_matches else '❌'} Entry: Manifest '{manifest.numero_entry}' {'=' if entry_matches else '≠'} Prefile '{prefile.numero_entry}'")

    # Broker
    broker_manifest = manifest.broker if manifest.broker != "NO_ENCONTRADO" else "NO_ENCONTRADO"
    broker_prefile = prefile.broker if prefile.broker != "NO_ENCONTRADO" else "NO_ENCONTRADO"
    broker_matches = broker_manifest != "NO_ENCONTRADO" and broker_prefile != "NO_ENCONTRADO"
    comparisons.append(ComparisonDetail(
        label="Broker",
        value1=broker_manifest,
        value2=broker_prefile,
        source1="Manifest",
        source2="Prefile",
        matches=broker_matches,
        icon="✅" if broker_matches else "❌"
    ))

    # Descripción
    desc_found = manifest.descripcion_mercancia != "NO_ENCONTRADO" and prefile.descripcion_mercancia != "NO_ENCONTRADO"
    if desc_found:
        details.append(f"✅ Descripción extraída de ambos documentos")
    else:
        details.append(f"❌ Descripción: Manifest '{manifest.descripcion_mercancia}' / Prefile '{prefile.descripcion_mercancia}'")

    # Cantidad
    cant_found = manifest.cantidad > 0 and prefile.cantidad > 0
    if cant_found:
        details.append(f"✅ Cantidad: Manifest {manifest.cantidad} / Prefile {prefile.cantidad}")
    else:
        details.append(f"❌ Cantidad: Manifest {manifest.cantidad} / Prefile {prefile.cantidad}")

    # Peso
    peso_found = manifest.peso_monto > 0 and prefile.peso_monto > 0
    if peso_found:
        details.append(f"✅ Peso: Manifest {manifest.peso_monto} / Prefile {prefile.peso_monto}")
    else:
        details.append(f"❌ Peso: Manifest {manifest.peso_monto} / Prefile {prefile.peso_monto}")

    if errors:
        return RuleValidationDetail(
            rule_id="R3",
            rule_name="Cruce Manifest vs Prefile",
            rule_description="Verifica consistencia entre E-Manifest y Prefile",
            status="warning" if len(errors) < 3 else "failed",
            icon="⚠️" if len(errors) < 3 else "❌",
            summary=f"Datos insuficientes para validación ({len(errors)} campos con problemas)",
            details=details,
            comparisons=comparisons,
            errors=errors,
            recommendation="Verificar manualmente los campos faltantes"
        )
    else:
        return RuleValidationDetail(
            rule_id="R3",
            rule_name="Cruce Manifest vs Prefile",
            rule_description="Verifica consistencia entre E-Manifest y Prefile",
            status="passed",
            icon="✅",
            summary="Todos los campos coinciden entre Manifest y Prefile",
            details=details,
            comparisons=comparisons,
            errors=[],
            recommendation=None
        )


def enhance_r4_validation(
    extracted_data: AllExtractedData
) -> RuleValidationDetail:
    """
    R4: Coincidencia de Aduana con detalle completo
    """
    logger.info("Generating enhanced R4 validation report...")

    error = validate_r4_aduana(extracted_data)

    seccion_doda = extracted_data.doda.seccion_aduanera
    aduana_manifest = extracted_data.manifest.aduana_arribo

    if error:
        return RuleValidationDetail(
            rule_id="R4",
            rule_name="Coincidencia de Aduana",
            rule_description="Verifica que la sección aduanera del DODA coincida con la aduana del Manifest",
            status="failed",
            icon="❌",
            summary="No se pudo validar coincidencia de aduanas",
            details=[
                f"❌ Sección Aduanera (DODA): {seccion_doda}",
                f"✅ Aduana de Arribo (Manifest): {aduana_manifest}",
                f"⚠️ No se puede comparar sin ambos valores"
            ],
            comparisons=[],
            errors=[error],
            recommendation="Verificar manualmente sección aduanera en DODA"
        )
    else:
        return RuleValidationDetail(
            rule_id="R4",
            rule_name="Coincidencia de Aduana",
            rule_description="Verifica que la sección aduanera del DODA coincida con la aduana del Manifest",
            status="passed",
            icon="✅",
            summary="Las aduanas coinciden",
            details=[
                f"✅ Sección Aduanera (DODA): {seccion_doda}",
                f"✅ Aduana de Arribo (Manifest): {aduana_manifest}",
                f"✓ Aduanas coinciden"
            ],
            comparisons=[
                ComparisonDetail(
                    label="Aduana",
                    value1=seccion_doda,
                    value2=aduana_manifest,
                    source1="DODA",
                    source2="Manifest",
                    matches=True,
                    icon="✅"
                )
            ],
            errors=[],
            recommendation=None
        )


def enhance_r5_validation(
    extracted_data: AllExtractedData,
    captured_data: CapturedData
) -> RuleValidationDetail:
    """
    R5: Coincidencia de Operador con detalle completo
    """
    logger.info("Generating enhanced R5 validation report...")

    driver_name = captured_data.driverData.name
    error = validate_r5_operador(extracted_data, driver_name)

    nombre_formulario = driver_name
    nombre_manifest = extracted_data.manifest.nombre_operador

    if error:
        return RuleValidationDetail(
            rule_id="R5",
            rule_name="Coincidencia de Operador",
            rule_description="Verifica que el operador del formulario coincida con el del manifiesto",
            status="failed",
            icon="❌",
            summary="El operador no coincide con el manifiesto",
            details=[
                f"❌ Formulario: {nombre_formulario}",
                f"❌ Manifest: {nombre_manifest}",
                f"⚠️ Los nombres no coinciden"
            ],
            comparisons=[
                ComparisonDetail(
                    label="Operador",
                    value1=nombre_formulario,
                    value2=nombre_manifest,
                    source1="Formulario",
                    source2="Manifest",
                    matches=False,
                    icon="❌"
                )
            ],
            errors=[error],
            recommendation="Verificar identidad del conductor"
        )
    else:
        return RuleValidationDetail(
            rule_id="R5",
            rule_name="Coincidencia de Operador",
            rule_description="Verifica que el operador del formulario coincida con el del manifiesto",
            status="passed",
            icon="✅",
            summary="El operador coincide con el manifiesto",
            details=[
                f"✅ Formulario: {nombre_formulario}",
                f"✅ Manifest: {nombre_manifest}",
                f"✓ Nombres coinciden (100%)"
            ],
            comparisons=[
                ComparisonDetail(
                    label="Operador",
                    value1=nombre_formulario,
                    value2=nombre_manifest,
                    source1="Formulario",
                    source2="Manifest",
                    matches=True,
                    similarity=1.0,
                    icon="✅"
                )
            ],
            errors=[],
            recommendation=None
        )


def validate_all_rules_enhanced(
    extracted_data: AllExtractedData,
    captured_data: CapturedData
) -> List[RuleValidationDetail]:
    """
    Ejecuta todas las validaciones y retorna detalles completos

    Args:
        extracted_data: Datos extraídos de documentos
        captured_data: Datos capturados del formulario

    Returns:
        Lista de RuleValidationDetail para las 5 reglas
    """
    logger.info("=" * 70)
    logger.info("ENHANCED VALIDATION: Generating detailed reports for all 5 rules")
    logger.info("=" * 70)

    rules = [
        enhance_r1_validation(extracted_data),
        enhance_r2_validation(extracted_data),
        enhance_r3_validation(extracted_data),
        enhance_r4_validation(extracted_data),
        enhance_r5_validation(extracted_data, captured_data)
    ]

    # Log summary
    passed = sum(1 for r in rules if r.status == "passed")
    failed = sum(1 for r in rules if r.status == "failed")
    warnings = sum(1 for r in rules if r.status == "warning")

    logger.info(f"Validation Summary: {passed} passed, {failed} failed, {warnings} warnings")
    logger.info("=" * 70)

    return rules
