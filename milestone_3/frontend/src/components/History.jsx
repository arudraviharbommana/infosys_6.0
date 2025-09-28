import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const History = ({ user }) => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/analyses');
      setAnalyses(response.data.analyses);
    } catch (error) {
      console.error('Error fetching analyses:', error);
      setError('Failed to load analysis history');
    } finally {
      setLoading(false);
    }
  };

  const handleViewAnalysis = (analysisId) => {
    navigate(`/result/${analysisId}`);
  };

  const handleDeleteAnalysis = async (analysisId) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try {
        await axios.delete(`/api/analysis/${analysisId}`);
        setAnalyses(analyses.filter(analysis => analysis.id !== analysisId));
      } catch (error) {
        console.error('Error deleting analysis:', error);
        alert('Failed to delete analysis');
      }
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'score-excellent';
    if (score >= 60) return 'score-good';
    if (score >= 40) return 'score-fair';
    return 'score-poor';
  };

  if (loading) {
    return (
      <div className="history-page">
        <div className="page-header">
          <h1>📁 Analysis History</h1>
          <p>Your resume analysis history - organized like folders</p>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your analysis history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-page">
        <div className="page-header">
          <h1>📁 Analysis History</h1>
          <p>Your resume analysis history - organized like folders</p>
        </div>
        <div className="error-container">
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <p>{error}</p>
            <button className="retry-button" onClick={fetchAnalyses}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <h1>📁 Analysis History</h1>
        <p>Your resume analysis history - organized like directory folders</p>
        <div className="history-stats">
          <span className="stat">Total: {analyses.length} analyses</span>
          <span className="stat">
            Avg Score: {analyses.length > 0 ? Math.round(analyses.reduce((sum, a) => sum + a.match_score, 0) / analyses.length) : 0}%
          </span>
        </div>
      </div>

      <div className="history-content">
        {analyses.length === 0 ? (
          <div className="empty-history">
            <div className="empty-icon">📂</div>
            <h3>No analysis history yet</h3>
            <p>Start by creating your first skill analysis!</p>
            <button 
              className="primary-button"
              onClick={() => navigate('/match')}
            >
              Create First Analysis
            </button>
          </div>
        ) : (
          <div className="directory-view">
            <div className="directory-header">
              <span className="folder-icon">📁</span>
              <span className="directory-path">~/SkillMatcher/Analyses/</span>
            </div>
            
            <div className="folder-contents">
              {analyses.map((analysis, index) => (
                <div key={analysis.id} className="folder-row">
                  <div className="folder-structure">
                    <span className="folder-line">├─</span>
                    <span className="folder-icon">📊</span>
                    <div className="folder-info">
                      <div className="folder-name">
                        Analysis_{analysis.id}_{formatDate(analysis.created_at).replace(/[/\s:,]/g, '_')}
                      </div>
                      <div className="folder-details">
                        <span className="file-count">2 files</span>
                        <span className="separator">•</span>
                        <span className={`match-score ${getScoreColor(analysis.match_score)}`}>
                          {analysis.match_score}% match
                        </span>
                        <span className="separator">•</span>
                        <span className="date">{formatDate(analysis.created_at)}</span>
                      </div>
                      <div className="folder-files">
                        <div className="file-entry">
                          <span className="file-line">│  ├─</span>
                          <span className="file-icon">📄</span>
                          <span className="file-name">resume.pdf</span>
                        </div>
                        <div className="file-entry">
                          <span className="file-line">│  └─</span>
                          <span className="file-icon">📋</span>
                          <span className="file-name">job_description.pdf</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="folder-actions">
                    <button
                      className="view-analysis-button"
                      onClick={() => handleViewAnalysis(analysis.id)}
                      title="View detailed analysis"
                    >
                      View Analysis
                    </button>
                    <button
                      className="delete-folder-button"
                      onClick={() => handleDeleteAnalysis(analysis.id)}
                      title="Delete analysis"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="directory-footer">
              <span className="folder-line">└─</span>
              <span className="summary">{analyses.length} analysis folders total</span>
            </div>
          </div>
        )}
      </div>

      <div className="history-actions">
        <button 
          className="primary-button"
          onClick={() => navigate('/match')}
        >
          🎯 New Analysis
        </button>
        <button 
          className="secondary-button"
          onClick={() => navigate('/dashboard')}
        >
          📊 Dashboard
        </button>
      </div>
    </div>
  );
};

export default History;