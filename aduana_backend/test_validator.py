"""
Test script for validation rules (R1-R5)
Tests the validator module without making OpenAI API calls
"""

from datetime import datetime, timedelta
from models.schemas import (
    AllExtractedData,
    ExtractedDODAData,
    ExtractedManifestData,
    ExtractedPrefileData,
    ExtractedPlateData,
    CapturedData,
    DriverData,
    Documents
)
from core.validator import validate_all_rules


def create_valid_data() -> tuple[AllExtractedData, CapturedData]:
    """
    Create a set of valid test data where all rules should pass
    """
    # Create extracted data that should pass all validations
    extracted_data = AllExtractedData(
        doda=ExtractedDODAData(
            fecha_emision=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),  # 1 day old (valid)
            seccion_aduanera="Tijuana"
        ),
        manifest=ExtractedManifestData(
            placa_tracto="ABC-123",
            placa_remolque="XYZ-789",
            nombre_operador="Juan Pérez García",
            aduana_arribo="Tijuana",
            numero_entry="ENT-2025-001234",
            broker="Brokers Unidos S.A.",
            descripcion_mercancia="Productos electrónicos",
            cantidad=100.0,
            peso_monto=5000.50
        ),
        prefile=ExtractedPrefileData(
            numero_entry="ENT-2025-001234",  # Matches manifest
            broker="Brokers Unidos S.A.",    # Matches manifest
            descripcion_mercancia="Productos electrónicos",  # Matches manifest
            cantidad=100.0,  # Matches manifest
            peso_monto=5000.50  # Matches manifest
        ),
        tractor_plate=ExtractedPlateData(
            plate_number="ABC-123",  # Matches manifest
            confidence=0.95
        ),
        trailer_plate=ExtractedPlateData(
            plate_number="XYZ-789",  # Matches manifest
            confidence=0.93
        )
    )

    # Create original captured data
    captured_data = CapturedData(
        driverData=DriverData(
            name="Juan Pérez García",  # Matches manifest
            tractorPlate="data:image/jpeg;base64,fake",
            trailerPlate="data:image/jpeg;base64,fake"
        ),
        documents=Documents(
            doda="data:image/jpeg;base64,fake",
            emanifest="data:image/jpeg;base64,fake",
            prefile="data:image/jpeg;base64,fake"
        )
    )

    return extracted_data, captured_data


def create_invalid_data_r1() -> tuple[AllExtractedData, CapturedData]:
    """
    Create test data that should fail R1 (DODA too old)
    """
    extracted_data, captured_data = create_valid_data()

    # Make DODA 5 days old (exceeds 3-day limit)
    extracted_data.doda.fecha_emision = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    return extracted_data, captured_data


def create_invalid_data_r2() -> tuple[AllExtractedData, CapturedData]:
    """
    Create test data that should fail R2 (plate mismatch)
    """
    extracted_data, captured_data = create_valid_data()

    # Mismatch tractor plate
    extracted_data.tractor_plate.plate_number = "WRONG-123"

    return extracted_data, captured_data


def create_invalid_data_r3() -> tuple[AllExtractedData, CapturedData]:
    """
    Create test data that should fail R3 (manifest/prefile mismatch)
    """
    extracted_data, captured_data = create_valid_data()

    # Mismatch entry number
    extracted_data.prefile.numero_entry = "DIFFERENT-ENTRY"

    return extracted_data, captured_data


def create_invalid_data_r4() -> tuple[AllExtractedData, CapturedData]:
    """
    Create test data that should fail R4 (customs mismatch)
    """
    extracted_data, captured_data = create_valid_data()

    # Mismatch customs
    extracted_data.manifest.aduana_arribo = "Mexicali"  # Different from Tijuana

    return extracted_data, captured_data


def create_invalid_data_r5() -> tuple[AllExtractedData, CapturedData]:
    """
    Create test data that should fail R5 (driver name mismatch)
    """
    extracted_data, captured_data = create_valid_data()

    # Mismatch driver name
    captured_data.driverData.name = "María González López"

    return extracted_data, captured_data


def run_test(test_name: str, extracted_data: AllExtractedData, captured_data: CapturedData, expected_errors: int):
    """
    Run a validation test and check results
    """
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")

    errors = validate_all_rules(extracted_data, captured_data)

    print(f"\nExpected errors: {expected_errors}")
    print(f"Actual errors: {len(errors)}")

    if len(errors) == expected_errors:
        print(f"[PASS] TEST PASSED")
        return True
    else:
        print(f"[FAIL] TEST FAILED")
        if errors:
            print("\nErrors found:")
            for error in errors:
                print(f"  [{error.rule_id}] {error.severity.upper()}: {error.message}")
        return False


if __name__ == "__main__":
    print("="*70)
    print("VALIDATION RULES TEST SUITE")
    print("="*70)

    results = []

    # Test 1: All rules should pass
    print("\n\n" + "="*70)
    print("TEST SUITE: Positive Case (All Valid)")
    print("="*70)
    extracted, captured = create_valid_data()
    result = run_test("All Rules Should Pass", extracted, captured, expected_errors=0)
    results.append(("All Valid", result))

    # Test 2: R1 should fail
    print("\n\n" + "="*70)
    print("TEST SUITE: Negative Cases (Individual Rule Failures)")
    print("="*70)
    extracted, captured = create_invalid_data_r1()
    result = run_test("R1 Failure: DODA Too Old", extracted, captured, expected_errors=1)
    results.append(("R1 Failure", result))

    # Test 3: R2 should fail
    extracted, captured = create_invalid_data_r2()
    result = run_test("R2 Failure: Plate Mismatch", extracted, captured, expected_errors=1)
    results.append(("R2 Failure", result))

    # Test 4: R3 should fail
    extracted, captured = create_invalid_data_r3()
    result = run_test("R3 Failure: Entry Number Mismatch", extracted, captured, expected_errors=1)
    results.append(("R3 Failure", result))

    # Test 5: R4 should fail
    extracted, captured = create_invalid_data_r4()
    result = run_test("R4 Failure: Customs Mismatch", extracted, captured, expected_errors=1)
    results.append(("R4 Failure", result))

    # Test 6: R5 should fail
    extracted, captured = create_invalid_data_r5()
    result = run_test("R5 Failure: Driver Name Mismatch", extracted, captured, expected_errors=1)
    results.append(("R5 Failure", result))

    # Summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n*** ALL TESTS PASSED! ***")
        exit(0)
    else:
        print(f"\n*** {total - passed} TEST(S) FAILED ***")
        exit(1)
