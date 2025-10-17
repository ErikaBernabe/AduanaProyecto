import React, { useRef, useState } from 'react';
import { FaCamera, FaImage, FaRedo } from 'react-icons/fa';
import '../styles/CameraCapture.css';

const CameraCapture = ({ onCapture, label }) => {
  const [preview, setPreview] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
        onCapture(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRecapture = () => {
    setPreview(null);
    onCapture(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openCamera = () => {
    if (fileInputRef.current) {
      fileInputRef.current.setAttribute('capture', 'environment');
      fileInputRef.current.click();
    }
  };

  const openGallery = () => {
    if (fileInputRef.current) {
      fileInputRef.current.removeAttribute('capture');
      fileInputRef.current.click();
    }
  };

  return (
    <div className="camera-capture">
      {label && <label className="camera-label">{label}</label>}

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {!preview ? (
        <div className="capture-options">
          <button
            type="button"
            className="capture-button camera-button"
            onClick={openCamera}
          >
            <FaCamera size={24} />
            <span>Tomar Foto</span>
          </button>
          <button
            type="button"
            className="capture-button gallery-button"
            onClick={openGallery}
          >
            <FaImage size={24} />
            <span>Seleccionar de Galería</span>
          </button>
        </div>
      ) : (
        <div className="preview-container">
          <img src={preview} alt="Preview" className="preview-image" />
          <button
            type="button"
            className="recapture-button"
            onClick={handleRecapture}
          >
            <FaRedo size={16} />
            <span>Recapturar</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default CameraCapture;
