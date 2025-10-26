import React, { useState } from 'react';
import DocumentList from '../components/DocumentList';
import DriverDataModal from '../components/DriverDataModal';
import DocumentCaptureModal from '../components/DocumentCaptureModal';
import { INITIAL_DOCUMENTS } from '../constants/documents';
import { useToast } from '../hooks/useToast';
import '../styles/InspectionScreen.css';

const InspectionScreen = () => {
  const toast = useToast();
  const [documents] = useState(INITIAL_DOCUMENTS);
  const [isDriverModalOpen, setIsDriverModalOpen] = useState(false);
  const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [isValidating, setIsValidating] = useState(false);

  // Estado para almacenar los datos capturados
  const [capturedData, setCapturedData] = useState({
    driverData: null,
    documents: {
      doda: null,
      emanifest: null,
      prefile: null
    }
  });

  const handleDocumentClick = (documentId) => {
    const doc = documents.find(d => d.id === documentId);

    if (documentId === 1) {
      // Abrir modal de datos del conductor
      setIsDriverModalOpen(true);
    } else {
      // Abrir modal de captura de documento
      setSelectedDocument(doc);
      setIsDocumentModalOpen(true);
    }
  };

  const handleSaveDriverData = (data) => {
    setCapturedData(prev => ({
      ...prev,
      driverData: data
    }));
    console.log('Datos del conductor guardados:', data);
  };

  const handleSaveDocument = (image) => {
    if (!selectedDocument) return;

    const documentKey = selectedDocument.name === 'DODA' ? 'doda'
      : selectedDocument.name === 'E-Manifest' ? 'emanifest'
      : 'prefile';

    setCapturedData(prev => ({
      ...prev,
      documents: {
        ...prev.documents,
        [documentKey]: image
      }
    }));

    console.log(`Documento ${selectedDocument.name} guardado`);
  };

  const isDocumentCompleted = (documentId) => {
    if (documentId === 1) {
      return capturedData.driverData !== null;
    } else if (documentId === 2) {
      return capturedData.documents.doda !== null;
    } else if (documentId === 3) {
      return capturedData.documents.emanifest !== null;
    } else if (documentId === 4) {
      return capturedData.documents.prefile !== null;
    }
    return false;
  };

  const completedCount = documents.filter(doc => isDocumentCompleted(doc.id)).length;
  const allCompleted = completedCount === documents.length;

  const handleValidateDocuments = async () => {
    if (!allCompleted) {
      toast.warning('Por favor completa todos los documentos antes de validar');
      return;
    }

    setIsValidating(true);

    try {
      // Get API URL from environment variable
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

      console.log('Enviando documentos al backend...', {
        driver: capturedData.driverData.name,
        apiUrl: API_URL
      });

      toast.info('Procesando documentos con IA... Esto puede tomar 30-60 segundos');

      // Make POST request to backend
      const response = await fetch(`${API_URL}/api/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(capturedData),
      });

      const result = await response.json();

      console.log('Respuesta del backend:', result);

      if (response.ok) {
        if (result.success) {
          // All validations passed
          toast.success(result.message || '✓ Todos los documentos son válidos');
        } else {
          // Validation failed - show errors
          const errorCount = result.errors?.length || 0;
          toast.error(`Se encontraron ${errorCount} error(es) de validación`);

          // Log errors to console for debugging
          if (result.errors && result.errors.length > 0) {
            console.log('Errores de validación:');
            result.errors.forEach(error => {
              console.log(`[${error.rule_id}] ${error.message}`);
            });

            // Show first error in detail
            const firstError = result.errors[0];
            setTimeout(() => {
              toast.warning(`${firstError.rule_id}: ${firstError.message}`);
            }, 1000);
          }
        }
      } else {
        // HTTP error
        toast.error(result.detail || 'Error al procesar los documentos');
        console.error('Error HTTP:', response.status, result);
      }

    } catch (error) {
      console.error('Error al conectar con el backend:', error);

      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        toast.error('No se pudo conectar con el servidor. Verifica que el backend esté corriendo en el puerto 8000');
      } else {
        toast.error('Error al validar documentos: ' + error.message);
      }
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <div className="inspection">
      <div className="inspection-header">
        <img src="/fronterainspeccion.png" alt="Logo Inspección" className="inspection-logo" />
        <h1>Inspección de Documentos</h1>
        <p className="inspection-subtitle">
          Sube o escanea los documentos requeridos para la exportación
        </p>
      </div>

      <div className="inspection-content">
        <DocumentList
          documents={documents}
          onDocumentClick={handleDocumentClick}
          isDocumentCompleted={isDocumentCompleted}
        />

        {completedCount > 0 && (
          <div className="progress-card">
            <div className="progress-info">
              <span className="progress-label">Progreso</span>
              <span className={`progress-count ${allCompleted ? 'all-completed' : ''}`}>
                {completedCount} / {documents.length}
              </span>
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${(completedCount / documents.length) * 100}%` }}
              />
            </div>
          </div>
        )}

        <button
          className={`validation ${allCompleted ? 'ready' : ''} ${isValidating ? 'validating' : ''}`}
          onClick={handleValidateDocuments}
          disabled={!allCompleted || isValidating}
        >
          {isValidating
            ? '⏳ Procesando con IA...'
            : allCompleted
              ? '✓ Validar Documentos'
              : 'Completa todos los documentos'}
        </button>
      </div>

      <DriverDataModal
        isOpen={isDriverModalOpen}
        onClose={() => setIsDriverModalOpen(false)}
        onSave={handleSaveDriverData}
        initialData={capturedData.driverData}
      />

      <DocumentCaptureModal
        isOpen={isDocumentModalOpen}
        onClose={() => {
          setIsDocumentModalOpen(false);
          setSelectedDocument(null);
        }}
        onSave={handleSaveDocument}
        documentName={selectedDocument?.name || ''}
        initialImage={selectedDocument ? capturedData.documents[
          selectedDocument.name === 'DODA' ? 'doda'
          : selectedDocument.name === 'E-Manifest' ? 'emanifest'
          : 'prefile'
        ] : null}
      />
    </div>
  );
};

export default InspectionScreen;
