"""
Aduana Proyecto - Backend API
FastAPI server for document validation at border crossings
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import tempfile
import shutil
import logging
from pathlib import Path

from models.schemas import CapturedData, ValidationResponse, AllExtractedData
from core.image_optimizer import optimize_image, save_optimized_image
from core.ocr_extractor import (
    extract_doda_data,
    extract_manifest_data,
    extract_prefile_data,
    extract_plate_data
)
from core.validator import validate_all_rules

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Aduana Proyecto API",
    description="API for validating border crossing documents",
    version="1.0.0"
)

# Configure CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Health check endpoint
    Returns the API status
    """
    return {
        "status": "ok",
        "message": "Aduana Proyecto API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Detailed health check endpoint
    """
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "port": os.getenv("BACKEND_PORT", "8000")
    }


@app.post("/api/validate", response_model=ValidationResponse)
async def validate_documents(data: CapturedData):
    """
    Main validation endpoint
    Receives document images from frontend, optimizes them, and validates

    Args:
        data: CapturedData object containing driver info and document images

    Returns:
        ValidationResponse with success status and any validation errors
    """
    temp_dir = None

    try:
        logger.info("=== Starting document validation ===")

        # Create temporary directory for this request
        temp_dir = tempfile.mkdtemp(prefix="aduana_")
        logger.info(f"Created temporary directory: {temp_dir}")

        # Track optimization results
        optimization_stats = {}

        # Optimize and save driver plate images
        logger.info("Processing driver plate images...")

        try:
            tractor_bytes, tractor_info = optimize_image(data.driverData.tractorPlate)
            tractor_path = os.path.join(temp_dir, "tractor_plate.jpg")
            save_optimized_image(tractor_bytes, tractor_path)
            optimization_stats['tractor_plate'] = tractor_info
            logger.info(f"✓ Tractor plate optimized: {tractor_info['saved_percentage']}% reduction")
        except Exception as e:
            logger.error(f"Error processing tractor plate: {e}")
            raise HTTPException(status_code=400, detail=f"Error procesando placa del tracto: {str(e)}")

        try:
            trailer_bytes, trailer_info = optimize_image(data.driverData.trailerPlate)
            trailer_path = os.path.join(temp_dir, "trailer_plate.jpg")
            save_optimized_image(trailer_bytes, trailer_path)
            optimization_stats['trailer_plate'] = trailer_info
            logger.info(f"✓ Trailer plate optimized: {trailer_info['saved_percentage']}% reduction")
        except Exception as e:
            logger.error(f"Error processing trailer plate: {e}")
            raise HTTPException(status_code=400, detail=f"Error procesando placa del remolque: {str(e)}")

        # Optimize and save document images
        logger.info("Processing document images...")

        try:
            doda_bytes, doda_info = optimize_image(data.documents.doda)
            doda_path = os.path.join(temp_dir, "doda.jpg")
            save_optimized_image(doda_bytes, doda_path)
            optimization_stats['doda'] = doda_info
            logger.info(f"✓ DODA optimized: {doda_info['saved_percentage']}% reduction")
        except Exception as e:
            logger.error(f"Error processing DODA: {e}")
            raise HTTPException(status_code=400, detail=f"Error procesando documento DODA: {str(e)}")

        try:
            emanifest_bytes, emanifest_info = optimize_image(data.documents.emanifest)
            emanifest_path = os.path.join(temp_dir, "emanifest.jpg")
            save_optimized_image(emanifest_bytes, emanifest_path)
            optimization_stats['emanifest'] = emanifest_info
            logger.info(f"✓ E-Manifest optimized: {emanifest_info['saved_percentage']}% reduction")
        except Exception as e:
            logger.error(f"Error processing E-Manifest: {e}")
            raise HTTPException(status_code=400, detail=f"Error procesando documento E-Manifest: {str(e)}")

        try:
            prefile_bytes, prefile_info = optimize_image(data.documents.prefile)
            prefile_path = os.path.join(temp_dir, "prefile.jpg")
            save_optimized_image(prefile_bytes, prefile_path)
            optimization_stats['prefile'] = prefile_info
            logger.info(f"✓ Prefile optimized: {prefile_info['saved_percentage']}% reduction")
        except Exception as e:
            logger.error(f"Error processing Prefile: {e}")
            raise HTTPException(status_code=400, detail=f"Error procesando documento Prefile: {str(e)}")

        # Calculate total statistics
        total_original = sum(stats['original_size'] for stats in optimization_stats.values())
        total_optimized = sum(stats['optimized_size'] for stats in optimization_stats.values())
        total_saved = total_original - total_optimized
        total_saved_percentage = (total_saved / total_original * 100) if total_original > 0 else 0

        logger.info(f"=== Optimization Complete ===")
        logger.info(f"Total images processed: 5")
        logger.info(f"Original size: {total_original:,} bytes")
        logger.info(f"Optimized size: {total_optimized:,} bytes")
        logger.info(f"Saved: {total_saved:,} bytes ({total_saved_percentage:.1f}%)")

        # ============================================================
        # Phase 3: Extract data using OpenAI Vision API
        # ============================================================
        logger.info("=== Starting AI Data Extraction ===")

        try:
            # Extract data from DODA
            logger.info("Extracting DODA data...")
            doda_data = extract_doda_data(doda_path)
            logger.info(f"✓ DODA data extracted: {doda_data.model_dump()}")

            # Extract data from E-Manifest
            logger.info("Extracting E-Manifest data...")
            manifest_data = extract_manifest_data(emanifest_path)
            logger.info(f"✓ E-Manifest data extracted: {manifest_data.model_dump()}")

            # Extract data from Prefile
            logger.info("Extracting Prefile data...")
            prefile_data = extract_prefile_data(prefile_path)
            logger.info(f"✓ Prefile data extracted: {prefile_data.model_dump()}")

            # Extract tractor plate number
            logger.info("Extracting tractor plate number...")
            tractor_plate_data = extract_plate_data(tractor_path)
            logger.info(f"✓ Tractor plate extracted: {tractor_plate_data.model_dump()}")

            # Extract trailer plate number
            logger.info("Extracting trailer plate number...")
            trailer_plate_data = extract_plate_data(trailer_path)
            logger.info(f"✓ Trailer plate extracted: {trailer_plate_data.model_dump()}")

            # Combine all extracted data
            extracted_data = AllExtractedData(
                doda=doda_data,
                manifest=manifest_data,
                prefile=prefile_data,
                tractor_plate=tractor_plate_data,
                trailer_plate=trailer_plate_data
            )

            logger.info("=== AI Data Extraction Complete ===")
            logger.info(f"All data extracted successfully")

        except Exception as e:
            logger.error(f"Error during AI data extraction: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error extrayendo datos con IA: {str(e)}"
            )

        # ============================================================
        # Phase 4: Validate extracted data using business rules (R1-R5)
        # ============================================================
        logger.info("=== Starting Business Rules Validation ===")

        try:
            # Execute all validation rules
            validation_errors = validate_all_rules(extracted_data, data)

            # Build response
            if validation_errors:
                # Validation failed - return errors
                error_count = len([e for e in validation_errors if e.severity == "error"])
                warning_count = len([e for e in validation_errors if e.severity == "warning"])

                if error_count > 0:
                    message = f"Se encontraron {error_count} error(es) de validación"
                    if warning_count > 0:
                        message += f" y {warning_count} advertencia(s)"
                else:
                    message = f"Se encontraron {warning_count} advertencia(s)"

                response = ValidationResponse(
                    success=False,
                    message=message,
                    errors=validation_errors
                )

                logger.warning(f"=== Validation FAILED: {message} ===")

            else:
                # All validations passed
                response = ValidationResponse(
                    success=True,
                    message=f"✓ Todos los documentos son válidos y consistentes. Conductor: {data.driverData.name}",
                    errors=[]
                )

                logger.info("=== Validation SUCCESSFUL - All rules passed ===")

        except Exception as e:
            logger.error(f"Error during validation: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error durante la validación: {str(e)}"
            )

        logger.info("=== Processing complete ===")

        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
