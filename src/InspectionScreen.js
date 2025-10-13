//Librerias
import './InspectionScreen.css'
import { FaFileAlt, FaRegFileAlt, FaRegFileImage } from 'react-icons/fa';
import React, { useEffect, useState } from 'react';
import { upload } from '@testing-library/user-event/dist/upload';

const InspectionScreen = () => {
  //Lista de documentos y status
  const [documents, setDocuments] = useState([
    { id: 1, name: 'Datos del conductor', icon: <FaRegFileImage />, upload: false },
    { id: 2, name: 'DODA', icon: <FaRegFileAlt />, upload: false },
    { id: 3, name: 'E-Manifest', icon: <FaRegFileAlt />, upload: false },
    { id: 4, name: 'Prefile', icon: <FaRegFileAlt />, upload: false },
  ]);

  // //Recibiendo datos del backend (Implementar despues)
  // useEffect(() => {
  //   fetch('API')
  //     .then(res => res.json())
  //     .then(fileBackend => {
  //       setDocuments(fileBackend);
  //     })
  // })

  const handleUpload = (documentId) => {
    console.log("Se hizo clic en el documento con ID:", documentId)
  }

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectDoc, setSelectDoc] = useState(null);

  //Estructura de la pagina 
  return (
    <div className="inspection">
      <h1>Inspección</h1>
      <p>Sube o escanea<br />los documentos.</p>
      <div className='document-list'>
        {documents.map((doc) => (
          <button key={doc.id} className='document-button' onClick={() => handleUpload(doc.id)}>
            <span className='icons'>{doc.icon}</span>
            {doc.name}
          </button>
        ))}
      </div>
      <button className='validation'>Validar documentos</button>
    </div>
  );
}

export default InspectionScreen