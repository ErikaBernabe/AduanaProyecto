import React from 'react';

const DocumentButton = ({ document, onClick }) => {
  return (
    <button
      className='document-button'
      onClick={() => onClick(document.id)}
    >
      <span className='icons'>{document.icon}</span>
      {document.name}
    </button>
  );
};

export default DocumentButton;
