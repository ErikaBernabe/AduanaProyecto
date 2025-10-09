import { useState } from 'react';
import './InspectionScreen.css'
import { FaFileAlt, FaRegFileAlt, FaRegFileImage } from 'react-icons/fa';

const InspectionScreen = () => {
  return (
    <div className="Inspection">
        <h1>Inspección</h1>
        <p>Sube o escanea<br/>los documentos.</p>
        <div className='Buttons'>
            <button className='Document-Button'><FaRegFileImage className='Icons'/>Datos del conductor</button>
            <button className='Document-Button'><FaRegFileAlt className='Icons'/>DODA</button>
            <button className='Document-Button'><FaRegFileAlt className='Icons'/>E-Manifest</button>
            <button className='Document-Button'><FaRegFileAlt className='Icons'/>Prefile</button>
        </div>
        <button className='Validation'>Validar documentos</button>
    </div>
  );
}

export default InspectionScreen