# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aduana Proyecto** is a React-based web application for customs border crossing document inspection. The app allows customs officers to scan/capture export documents using OCR or similar technology, validate data consistency, and prevent errors before vehicles reach the border crossing.

## Development Commands

### Frontend (React)

```bash
# Install dependencies
npm install

# Start development server (runs on http://localhost:3000)
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Backend (FastAPI)

```bash
# Navigate to backend directory
cd aduana_backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server (http://localhost:8000)
uvicorn main:app --reload

# Run tests
python test_api.py          # API endpoint tests
python test_extraction.py   # OCR extraction tests
python test_validator.py    # Business rules validation tests
```

## Architecture

### Application Flow
The app uses a simple authentication flow:
1. **LoginScreen** → User logs in (currently no backend validation)
2. **InspectionScreen** → Main document inspection interface

State is managed at the App level with `useState` for authentication (`isLoggedIn`).

### Core State Management

**ToastContext** ([src/contexts/ToastContext.js](src/contexts/ToastContext.js))
- Global toast notification system
- Access via `useToast()` hook from [src/hooks/useToast.js](src/hooks/useToast.js)
- Supports three types: `success`, `warning`, `error`
- Usage: `toast.success('message')`, `toast.warning('message')`, `toast.error('message')`

**Document State** ([src/pages/InspectionScreen.js](src/pages/InspectionScreen.js))
- All captured data stored in `capturedData` state object with structure:
  ```javascript
  {
    driverData: { name, tractorPlate, trailerPlate },
    documents: { doda, emanifest, prefile }
  }
  ```
- Document definitions in [src/constants/documents.js](src/constants/documents.js)

### Component Organization

**Pages**
- `LoginScreen` - Simple email/password form using React Hook Form
- `InspectionScreen` - Main document management interface with progress tracking

**Modal Components**
- `DriverDataModal` - Captures driver name + 2 license plate photos (tractor and trailer)
- `DocumentCaptureModal` - Generic document photo capture (DODA, E-Manifest, Prefile)
- `Modal` - Base modal wrapper component

**Capture Component**
- `CameraCapture` - Dual-purpose image capture:
  - "Tomar Foto" button - Opens camera (mobile) via `capture="environment"` attribute
  - "Seleccionar de Galería" button - Opens file picker
  - Stores images as base64 data URLs

**UI Components**
- `DocumentList` - Displays document buttons with completion status
- `DocumentButton` - Individual document button with icon and checkmark when completed
- `Toast/ToastContainer` - Notification system UI

### Form Handling

- **Login form**: Uses `react-hook-form` with `register` and `handleSubmit`
- **Modal forms**: Controlled components with local state (`useState`)
- **Validation**: Client-side validation with toast notifications for missing fields

### Image Handling

All images (driver plates, documents) are:
1. Captured via file input (`<input type="file" accept="image/*">`)
2. Read using FileReader API
3. Stored as base64 data URLs in component state
4. Displayed in preview using `<img src={base64String} />`

### Styling

- CSS modules pattern: Each component has corresponding CSS file in [src/styles/](src/styles/)
- No CSS-in-JS or styled-components
- All styles use plain CSS classes

### Important Implementation Details

**Document ID Mapping**:
- ID 1 = "Datos del conductor" (driver data modal)
- ID 2 = "DODA" (document capture)
- ID 3 = "E-Manifest" (document capture)
- ID 4 = "Prefile" (document capture)

**Progress Tracking**:
- Progress bar appears after first document completion
- Validation button enables only when all 4 items completed
- Completion logic in `isDocumentCompleted(documentId)` function

**Validation Flow**:
- Triggered when all 4 documents are completed and "Validar Documentos" button is clicked
- Sends `capturedData` object to backend `/api/validate` endpoint
- Backend processes images with AI and validates using business rules (R1-R5)
- Results displayed via toast notifications

## Environment Variables

The project uses a `.env` file (gitignored) in the root directory containing:

**Backend Variables**:
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o Vision OCR/document processing
- `FRONTEND_URL` - (optional) Frontend URL for CORS, defaults to `http://localhost:3000`
- `BACKEND_PORT` - (optional) Backend port, defaults to `8000`
- `BACKEND_HOST` - (optional) Backend host, defaults to `0.0.0.0`

**Frontend Variables**:
- `REACT_APP_API_URL` - Backend API URL, defaults to `http://localhost:8000`

## Assets

Logo files in [public/](public/):
- `frontera.png` - Login screen logo
- `fronterainspeccion.png` - Inspection screen logo

## Technology Stack

### Frontend
- **React 19.2.0** - UI library
- **React Hook Form 7.64.0** - Form management (currently only used in LoginScreen)
- **React Icons 5.5.0** - Icon library (FaRegFileAlt, FaRegFileImage, FaCamera, etc.)
- **Create React App 5.0.1** - Build tooling
- **React Testing Library** - Testing framework

### Backend
- **FastAPI 0.104.1** - Modern Python web framework
- **Uvicorn 0.24.0** - ASGI server
- **OpenAI 1.58.1** - GPT-4o Vision API for OCR/document extraction
- **Pillow 10.1.0** - Image processing and optimization
- **Pydantic** - Data validation via FastAPI
- **python-dotenv 1.0.0** - Environment variable management

## Backend Architecture (FastAPI)

### Project Structure

```
aduana_backend/
├── main.py                 # FastAPI app entry point, endpoints, request handling
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (gitignored)
├── core/                   # Core business logic modules
│   ├── image_optimizer.py  # Image optimization (base64→PIL→optimized JPEG)
│   ├── ocr_extractor.py    # OpenAI GPT-4o Vision API integration
│   └── validator.py        # Business rules validation (R1-R5)
├── models/
│   └── schemas.py          # Pydantic models for request/response validation
└── test_*.py               # Test files for various components
```

### Core Modules

**[main.py](aduana_backend/main.py)** - FastAPI application
- **Endpoints**:
  - `GET /` - Health check
  - `GET /health` - Detailed health with OpenAI config status
  - `POST /api/validate` - Main validation endpoint
- **Processing pipeline**:
  1. Image optimization (base64 → optimized JPEG files)
  2. AI data extraction (OpenAI Vision API)
  3. Business rules validation (R1-R5)
  4. Cleanup temporary files

**[core/image_optimizer.py](aduana_backend/core/image_optimizer.py)**
- Decodes base64 images from frontend
- Optimizes images (resizes, compresses) to reduce API costs
- Saves optimized images to temporary directory
- Logs optimization statistics (original vs optimized size)

**[core/ocr_extractor.py](aduana_backend/core/ocr_extractor.py)**
- Integrates with OpenAI GPT-4o Vision API
- Functions for each document type:
  - `extract_doda_data()` - Extracts DODA fields (fecha_elaboracion, aduana)
  - `extract_manifest_data()` - Extracts manifest fields (placas, operador, aduana, etc.)
  - `extract_prefile_data()` - Extracts prefile fields (entry, broker, items)
  - `extract_plate_data()` - Extracts plate numbers from photos
- Uses structured JSON responses via OpenAI's response_format
- Returns Pydantic models for type safety

**[core/validator.py](aduana_backend/core/validator.py)**
- Implements 5 business validation rules:
  - **R1**: DODA vigencia (max 3 days old)
  - **R2**: Plate matching (Manifest vs photos)
  - **R3**: Manifest/Prefile cross-validation (Entry, Broker, Description, Quantity, Weight)
  - **R4**: Customs matching (DODA vs Manifest)
  - **R5**: Operator matching (Manifest vs form input)
- Each rule is a separate function returning `ValidationError` list
- `validate_all_rules()` orchestrates all validations

**[models/schemas.py](aduana_backend/models/schemas.py)**
- Pydantic models for type-safe API contracts:
  - `CapturedData` - Frontend request structure
  - `DodaData`, `ManifestData`, `PrefileData`, `PlateData` - Extracted document data
  - `ValidationError` - Error details (rule, field, severity, message)
  - `ValidationResponse` - API response structure

### Backend API Integration

- **URL**: Configured via `REACT_APP_API_URL` environment variable (default: `http://localhost:8000`)
- **Main Endpoint**: `POST /api/validate`
  - Receives `capturedData` with driver info and all document images (base64)
  - Returns `ValidationResponse` with success status and error list

### Validation Rules (R1-R5)

1. **R1**: DODA vigencia (max 3 días de antigüedad)
2. **R2**: Coincidencia de placas (Manifiesto vs fotos)
3. **R3**: Cruce Manifest/Prefile (Entry, Broker, Descripción, Cantidad, Peso)
4. **R4**: Coincidencia de aduana (DODA vs Manifiesto)
5. **R5**: Coincidencia de operador (Manifiesto vs formulario)

### Frontend Integration

- **File**: [src/pages/InspectionScreen.js](src/pages/InspectionScreen.js)
- **Function**: `handleValidateDocuments()` - Async function that POSTs to backend
- **Loading State**: `isValidating` state shows "Procesando con IA..." during API call
- **Error Handling**: Displays toast notifications for success/errors
- **Response Processing**:
  - Success: Shows success toast
  - Validation errors: Shows error count + first error detail
  - Network errors: Shows connection error message

### Running the Full Stack

**Backend**:
```bash
cd aduana_backend
venv\Scripts\activate  # Windows
uvicorn main:app --reload
```

**Frontend**:
```bash
npm start
```

Access at: http://localhost:3000

## Known TODOs

1. ~~Backend integration for document validation~~ ✅ COMPLETED
2. Actual authentication implementation (LoginScreen currently accepts any input)
3. ~~OCR/document text extraction using OpenAI API~~ ✅ COMPLETED
4. Persistent storage (currently all data lost on page refresh)
5. Detailed error display modal (currently only shows first error in toast)
