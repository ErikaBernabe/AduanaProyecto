import { useState } from 'react';
import './InspectionScreen.css'

const InspectionScreen = () => {
  return (
    <div className="Inspection">
        <h1>Inspección</h1>
        <p>Sube o escanea<br/>los documentos.</p>
        <div className='Buttons'>
            <button id='Document'>Datos del conductor</button>
            <button id='Document'>DODA</button>
            <button id='Document'>E-Manifest</button>
            <button id='Document'>Prefile</button>
        </div>
        <button className='Validation'>Validar documentos</button>
    </div>
  );
}

export default InspectionScreen