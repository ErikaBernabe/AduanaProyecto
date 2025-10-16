import React, { useState } from 'react';
import DocumentList from '../components/DocumentList';
import { INITIAL_DOCUMENTS } from '../constants/documents';
import '../styles/InspectionScreen.css';

const InspectionScreen = () => {
  const [documents] = useState(INITIAL_DOCUMENTS);
  // const [isModalOpen, setIsModalOpen] = useState(false);
  // const [selectedDoc, setSelectedDoc] = useState(null);

  const handleDocumentClick = (documentId) => {
    console.log("Se hizo clic en el documento con ID:", documentId);
    // TODO: Implementar modal para subida de archivos
    // const doc = documents.find(doc => doc.id === documentId);
    // setSelectedDoc(doc);
    // setIsModalOpen(true);
  };

  const handleValidateDocuments = () => {
    console.log("Validando documentos...");
    // Lógica para validar documentos
  };

  // Para implementar después: conexión con el backend
  // useEffect(() => {
  //   fetch('API_URL')
  //     .then(res => res.json())
  //     .then(fileBackend => {
  //       setDocuments(fileBackend);
  //     })
  //     .catch(error => console.error('Error fetching documents:', error));
  // }, []);

  return (
    <div className="inspection">
      <h1>Inspección</h1>
      <p>
        Sube o escanea<br />
        los documentos.
      </p>

      <DocumentList
        documents={documents}
        onDocumentClick={handleDocumentClick}
      />

      <button className='validation' onClick={handleValidateDocuments}>
        Validar documentos
      </button>
    </div>
  );
};

export default InspectionScreen;
