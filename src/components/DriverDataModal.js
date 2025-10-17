import React, { useState } from 'react';
import Modal from './Modal';
import CameraCapture from './CameraCapture';
import { useToast } from '../hooks/useToast';
import '../styles/DriverDataModal.css';

const DriverDataModal = ({ isOpen, onClose, onSave, initialData }) => {
  const [driverName, setDriverName] = useState(initialData?.name || '');
  const [tractorPlate, setTractorPlate] = useState(initialData?.tractorPlate || null);
  const [trailerPlate, setTrailerPlate] = useState(initialData?.trailerPlate || null);
  const toast = useToast();

  const handleSave = () => {
    if (!driverName.trim()) {
      toast.warning('Por favor ingresa el nombre del operador');
      return;
    }
    if (!tractorPlate) {
      toast.warning('Por favor captura la foto de la placa del tracto');
      return;
    }
    if (!trailerPlate) {
      toast.warning('Por favor captura la foto de la placa del remolque');
      return;
    }

    onSave({
      name: driverName.trim(),
      tractorPlate,
      trailerPlate
    });

    onClose();
  };

  const handleCancel = () => {
    setDriverName(initialData?.name || '');
    setTractorPlate(initialData?.tractorPlate || null);
    setTrailerPlate(initialData?.trailerPlate || null);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleCancel} title="Datos del Conductor">
      <div className="driver-data-form">
        <div className="form-group">
          <label className="form-label">Nombre del Operador *</label>
          <input
            type="text"
            className="form-input"
            placeholder="Ingresa el nombre completo"
            value={driverName}
            onChange={(e) => setDriverName(e.target.value)}
          />
        </div>

        <div className="plates-container">
          <div className="plate-section">
            <CameraCapture
              label="Placa del Tracto *"
              onCapture={setTractorPlate}
            />
          </div>

          <div className="plate-section">
            <CameraCapture
              label="Placa del Remolque *"
              onCapture={setTrailerPlate}
            />
          </div>
        </div>

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
            Guardar Datos
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default DriverDataModal;
