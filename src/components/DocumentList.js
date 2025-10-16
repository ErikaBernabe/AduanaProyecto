import React from 'react';
import DocumentButton from './DocumentButton';

const DocumentList = ({ documents, onDocumentClick }) => {
  return (
    <div className='document-list'>
      {documents.map((doc) => (
        <DocumentButton
          key={doc.id}
          document={doc}
          onClick={onDocumentClick}
        />
      ))}
    </div>
  );
};

export default DocumentList;
