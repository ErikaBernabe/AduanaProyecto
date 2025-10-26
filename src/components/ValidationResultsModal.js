import React, { useState } from 'react';
import '../styles/ValidationResultsModal.css';

const ValidationResultsModal = ({ isOpen, onClose, validationData }) => {
  const [expandedSections, setExpandedSections] = useState({
    rules: true,
    extraction: false,
    technical: false
  });

  if (!isOpen || !validationData) return null;

  const { summary, rules, extraction, timestamp } = validationData;

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return '#4caf50';
      case 'partial': return '#ff9800';
      case 'failed': return '#f44336';
      default: return '#757575';
    }
  };

  const getRuleStatusColor = (status) => {
    switch (status) {
      case 'passed': return '#4caf50';
      case 'failed': return '#f44336';
      case 'warning': return '#ff9800';
      default: return '#757575';
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content validation-modal" onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div className="modal-header">
          <h2>✓ Resultados de Validación</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">

          {/* Summary Section */}
          <div className="summary-card">
            <h3>📊 RESUMEN GENERAL</h3>
            <div className="summary-content">
              <div className="summary-status">
                <span
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(summary.overall_status) }}
                >
                  {summary.overall_status === 'success' ? '✅ Validación Exitosa' :
                   summary.overall_status === 'partial' ? '⚠️ Validación Parcial' :
                   '❌ Validación Fallida'}
                </span>
              </div>

              <div className="summary-stats">
                <div className="stat-row">
                  <label>✅ Reglas Pasadas:</label>
                  <div className="stat-bar-container">
                    <div className="stat-bar">
                      <div
                        className="stat-bar-fill success"
                        style={{ width: `${(summary.passed_rules / summary.total_rules) * 100}%` }}
                      ></div>
                    </div>
                    <span className="stat-value">{summary.passed_rules}/{summary.total_rules} ({Math.round((summary.passed_rules / summary.total_rules) * 100)}%)</span>
                  </div>
                </div>

                <div className="stat-row">
                  <label>❌ Reglas Fallidas:</label>
                  <div className="stat-bar-container">
                    <div className="stat-bar">
                      <div
                        className="stat-bar-fill error"
                        style={{ width: `${(summary.failed_rules / summary.total_rules) * 100}%` }}
                      ></div>
                    </div>
                    <span className="stat-value">{summary.failed_rules}/{summary.total_rules} ({Math.round((summary.failed_rules / summary.total_rules) * 100)}%)</span>
                  </div>
                </div>

                {summary.warning_rules > 0 && (
                  <div className="stat-row">
                    <label>⚠️ Advertencias:</label>
                    <span className="stat-value">{summary.warning_rules}</span>
                  </div>
                )}

                <div className="stat-row">
                  <label>🎯 Confianza IA:</label>
                  <div className="stat-bar-container">
                    <div className="stat-bar">
                      <div
                        className="stat-bar-fill confidence"
                        style={{ width: `${summary.confidence_average * 100}%` }}
                      ></div>
                    </div>
                    <span className="stat-value">
                      {Math.round(summary.confidence_average * 100)}%
                      ({summary.confidence_average >= 0.8 ? 'ALTA' :
                         summary.confidence_average >= 0.6 ? 'MEDIA' : 'BAJA'})
                    </span>
                  </div>
                </div>

                <div className="stat-row">
                  <label>⏱️ Tiempo Procesado:</label>
                  <span className="stat-value">{summary.processing_time}s</span>
                </div>
              </div>
            </div>
          </div>

          {/* Rules Section */}
          <div className="section-card">
            <div className="section-header" onClick={() => toggleSection('rules')}>
              <h3>📋 VALIDACIONES POR REGLA</h3>
              <button className="toggle-button">
                {expandedSections.rules ? '▼ Colapsar' : '▶ Expandir'}
              </button>
            </div>

            {expandedSections.rules && (
              <div className="section-content">
                {rules.map((rule, index) => (
                  <RuleCard key={rule.rule_id} rule={rule} />
                ))}
              </div>
            )}
          </div>

          {/* Extraction Section */}
          <div className="section-card">
            <div className="section-header" onClick={() => toggleSection('extraction')}>
              <h3>🔍 EXTRACCIÓN DE DATOS (IA)</h3>
              <button className="toggle-button">
                {expandedSections.extraction ? '▼ Colapsar' : '▶ Expandir'}
              </button>
            </div>

            {expandedSections.extraction && (
              <div className="section-content">
                {extraction.map((doc, index) => (
                  <ExtractionCard key={`${doc.document_type}-${index}`} document={doc} />
                ))}
              </div>
            )}
          </div>

          {/* Technical Info Section */}
          <div className="section-card">
            <div className="section-header" onClick={() => toggleSection('technical')}>
              <h3>⚙️ INFORMACIÓN TÉCNICA</h3>
              <button className="toggle-button">
                {expandedSections.technical ? '▼ Colapsar' : '▶ Expandir'}
              </button>
            </div>

            {expandedSections.technical && (
              <div className="section-content technical-info">
                <p><strong>Modelo IA:</strong> gpt-4o-mini</p>
                <p><strong>Modo de Detalle:</strong> high (768px)</p>
                <p><strong>Optimización:</strong> Activa (768px, JPEG 85, sin grayscale)</p>
                <p><strong>Timestamp:</strong> {new Date(timestamp).toLocaleString('es-MX')}</p>
                <p><strong>Tiempo de Proceso:</strong> {summary.processing_time} segundos</p>
                <div className="technical-note">
                  ⚠️ <strong>NOTA:</strong> El sistema usa modo "high" detail para mejor precisión de extracción de texto pequeño.
                </div>
              </div>
            )}
          </div>

        </div>

        {/* Footer Actions */}
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            ✓ Cerrar
          </button>
        </div>

      </div>
    </div>
  );
};

// Rule Card Component
const RuleCard = ({ rule }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={`rule-card rule-${rule.status}`}>
      <div className="rule-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="rule-title">
          <span className="rule-icon">{rule.icon}</span>
          <span className="rule-id">{rule.rule_id}:</span>
          <span className="rule-name">{rule.rule_name}</span>
        </div>
        <button className="expand-toggle">{isExpanded ? '▲' : '▼'}</button>
      </div>

      <div className="rule-summary">{rule.summary}</div>

      {isExpanded && (
        <div className="rule-details">
          <p className="rule-description">{rule.rule_description}</p>

          {rule.details && rule.details.length > 0 && (
            <div className="details-list">
              {rule.details.map((detail, i) => (
                <div key={i} className="detail-item">{detail}</div>
              ))}
            </div>
          )}

          {rule.comparisons && rule.comparisons.length > 0 && (
            <div className="comparisons-table">
              <h4>Comparaciones:</h4>
              <table>
                <thead>
                  <tr>
                    <th>Campo</th>
                    <th>Valor 1 ({rule.comparisons[0].source1})</th>
                    <th>Valor 2 ({rule.comparisons[0].source2})</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {rule.comparisons.map((comp, i) => (
                    <tr key={i}>
                      <td>{comp.label}</td>
                      <td>{comp.value1}</td>
                      <td>{comp.value2}</td>
                      <td className="comparison-icon">{comp.icon}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {rule.recommendation && (
            <div className="recommendation">
              <strong>Recomendación:</strong> {rule.recommendation}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Extraction Card Component
const ExtractionCard = ({ document }) => {
  return (
    <div className="extraction-card">
      <div className="extraction-header">
        <h4>{document.document_name}</h4>
        <div className="confidence-badge">
          {Math.round(document.confidence_score * 100)}%
        </div>
      </div>

      <div className="confidence-bar-container">
        <div className="confidence-bar">
          <div
            className="confidence-bar-fill"
            style={{
              width: `${document.confidence_score * 100}%`,
              backgroundColor: document.confidence_score >= 0.8 ? '#4caf50' :
                             document.confidence_score >= 0.6 ? '#ff9800' : '#f44336'
            }}
          ></div>
        </div>
        <span className="confidence-text">
          ({document.extracted_fields}/{document.total_fields} campos extraídos)
        </span>
      </div>

      <div className="fields-list">
        {document.fields.map((field, i) => (
          <div key={i} className={`field-row field-${field.status}`}>
            <span className="field-icon">{field.icon}</span>
            <span className="field-label">{field.label}:</span>
            <span className="field-value">{field.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ValidationResultsModal;
