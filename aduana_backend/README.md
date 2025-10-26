# Aduana Proyecto - Backend API

Backend API built with FastAPI for validating border crossing documents.

## Project Structure

```
aduana_backend/
├── core/               # Business logic and utilities
├── models/            # Pydantic schemas and data models
├── uploads/           # Temporary file storage
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (not in git)
└── README.md         # This file
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000
```

## Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```

Or using Python:

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Health Check

- **GET /** - Basic health check
  ```json
  {
    "status": "ok",
    "message": "Aduana Proyecto API is running",
    "version": "1.0.0"
  }
  ```

- **GET /health** - Detailed health check
  ```json
  {
    "status": "healthy",
    "openai_configured": true,
    "port": "8000"
  }
  ```

### Document Validation (Phase 2)

- **POST /api/validate** - Main validation endpoint
  - Accepts `CapturedData` JSON with driver info and document images
  - Optimizes all images (2 plates + 3 documents)
  - Returns `ValidationResponse` with success status and errors

  **Request Body:**
  ```json
  {
    "driverData": {
      "name": "Juan Pérez",
      "tractorPlate": "data:image/png;base64,...",
      "trailerPlate": "data:image/png;base64,..."
    },
    "documents": {
      "doda": "data:image/jpeg;base64,...",
      "emanifest": "data:image/jpeg;base64,...",
      "prefile": "data:image/jpeg;base64,..."
    }
  }
  ```

  **Response:**
  ```json
  {
    "success": true,
    "message": "Documentos recibidos y optimizados correctamente",
    "errors": []
  }
  ```

## Testing

You can test the API using curl:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/health
```

Or run the included test script:

```bash
python test_api.py
```

Or visit the interactive API documentation at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Dependencies

- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server
- **python-dotenv** - Environment variable management
- **OpenAI** - AI/OCR integration
- **Pillow** - Image processing
- **python-multipart** - File upload support

## Development Status

✅ **Phase 1: Backend Project Foundation** - COMPLETED
- [x] Project structure created
- [x] Virtual environment configured
- [x] Dependencies installed
- [x] Basic FastAPI server running
- [x] Health check endpoints functional

✅ **Phase 2: Data Flow and Image Optimization** - COMPLETED
- [x] Pydantic schemas created (CapturedData, ValidationResponse)
- [x] Image optimizer module with base64 decoding
- [x] Image resizing (max 1024px) and compression (JPEG quality 85%)
- [x] POST /api/validate endpoint functional
- [x] Temporary file handling with automatic cleanup
- [x] Comprehensive error handling and logging
- [x] Test script created and validated

✅ **Phase 3: AI Connection for Data Extraction** - COMPLETED
- [x] OpenAI GPT-4o Vision integration
- [x] Extraction schemas for all document types (DODA, Manifest, Prefile, Plates)
- [x] Specialized prompts for each document type
- [x] OCR extraction from 5 images (3 documents + 2 license plates)
- [x] Retry logic with exponential backoff
- [x] JSON parsing from AI responses with error handling
- [x] Complete AllExtractedData model combining all results
- [x] Integration in /api/validate endpoint
- [x] Test script with realistic text documents

✅ **Phase 4: Implementing the Brain (The Rules)** - COMPLETED
- [x] Validator module with all 5 business rules (R1-R5)
- [x] R1: DODA Vigencia (max 3 days old)
- [x] R2: License plate matching (Manifest vs Photos)
- [x] R3: Cross-check Manifest vs Prefile (Entry, Broker, Description, Quantity, Weight)
- [x] R4: Customs matching (DODA vs Manifest)
- [x] R5: Driver name matching (Manifest vs User input)
- [x] Fuzzy string matching with normalization
- [x] Comprehensive error messages in Spanish
- [x] Integration in /api/validate endpoint
- [x] Unit tests for all rules (6/6 tests passing)
- [x] Severity levels (error/warning)
- [x] Detailed logging for each validation

✅ **Phase 5: Final Connection and User Experience** - COMPLETED
- [x] CORS configuration for React frontend (http://localhost:3000)
- [x] Environment variable configuration (.env)
- [x] Complete end-to-end integration tested
- [x] Frontend integration in InspectionScreen.js
- [x] Loading states and error handling in UI
- [x] Toast notifications for user feedback
- [x] Full documentation in CLAUDE.md

## 🎉 Project Status: COMPLETE

All 5 phases have been successfully completed. The application is fully functional end-to-end:

1. ✅ Backend infrastructure with FastAPI
2. ✅ Image optimization pipeline
3. ✅ AI data extraction with GPT-4o Vision
4. ✅ Business rules validation (R1-R5)
5. ✅ Frontend-backend integration

### Quick Start (Full Stack)

1. **Start Backend** (Terminal 1):
   ```bash
   cd aduana_backend
   uvicorn main:app --reload
   ```

2. **Start Frontend** (Terminal 2):
   ```bash
   cd ..
   npm start
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
