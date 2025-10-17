import React from 'react';
import DocumentButton from './DocumentButton';

const DocumentList = ({ documents, onDocumentClick, isDocumentCompleted }) => {
  return (
    <div className='document-list'>
      {documents.map((doc) => (
        <DocumentButton
          key={doc.id}
          document={doc}
          onClick={onDocumentClick}
          isCompleted={isDocumentCompleted(doc.id)}
        />
      ))}
    </div>
  );
};

export default DocumentList;
