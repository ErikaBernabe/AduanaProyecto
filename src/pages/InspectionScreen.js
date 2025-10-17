import React, { useState } from 'react';
import DocumentList from '../components/DocumentList';
import DriverDataModal from '../components/DriverDataModal';
import DocumentCaptureModal from '../components/DocumentCaptureModal';
import { INITIAL_DOCUMENTS } from '../constants/documents';
import '../styles/InspectionScreen.css';

const InspectionScreen = () => {
  const [documents] = useState(INITIAL_DOCUMENTS);
  const [isDriverModalOpen, setIsDriverModalOpen] = useState(false);
  const [isDocumentModalOpen, setIsDocumentModalOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState(null);

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

  const handleValidateDocuments = () => {
    if (!allCompleted) {
      alert('Por favor completa todos los documentos antes de validar');
      return;
    }
    console.log("Validando documentos...", capturedData);
    // TODO: Lógica para validar documentos con el backend
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
          className={`validation ${allCompleted ? 'ready' : ''}`}
          onClick={handleValidateDocuments}
          disabled={!allCompleted}
        >
          {allCompleted ? '✓ Validar Documentos' : 'Completa todos los documentos'}
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
