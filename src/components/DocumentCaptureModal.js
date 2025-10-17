import React, { useState } from 'react';
import Modal from './Modal';
import CameraCapture from './CameraCapture';
import '../styles/DocumentCaptureModal.css';

const DocumentCaptureModal = ({ isOpen, onClose, onSave, documentName, initialImage }) => {
  const [capturedImage, setCapturedImage] = useState(initialImage || null);

  const handleSave = () => {
    if (!capturedImage) {
      alert(`Por favor captura la foto del documento ${documentName}`);
      return;
    }

    onSave(capturedImage);
    onClose();
  };

  const handleCancel = () => {
    setCapturedImage(initialImage || null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleCancel} title={`Capturar ${documentName}`}>
      <div className="document-capture-form">
        <p className="document-instruction">
          Por favor captura una foto clara del documento <strong>{documentName}</strong>
        </p>

        <CameraCapture
          onCapture={setCapturedImage}
        />

        <div className="form-actions">
          <button
            type="button"
            className="btn-cancel"
            onClick={handleCancel}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-save"
            onClick={handleSave}
          >
            Guardar Documento
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default DocumentCaptureModal;
