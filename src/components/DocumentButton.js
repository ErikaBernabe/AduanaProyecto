import React from 'react';
import { FaCheck } from 'react-icons/fa';

const DocumentButton = ({ document, onClick, isCompleted }) => {
  return (
    <button
      className={`document-button ${isCompleted ? 'completed' : ''}`}
      onClick={() => onClick(document.id)}
    >
      <span className='icons'>{document.icon}</span>
      {document.name}
      {isCompleted && (
        <span className='check-icon'>
          <FaCheck />
        </span>
      )}
    </button>
  );
};

export default DocumentButton;
