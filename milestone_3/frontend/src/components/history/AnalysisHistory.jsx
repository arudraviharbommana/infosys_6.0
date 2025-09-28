import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AnalysisFolder = ({ analysis, onView, onDelete }) => {
    const [isExpanded, setIsExpanded] = useState(false);

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

    const toggleExpanded = () => {
        setIsExpanded(!isExpanded);
    };

    return (
        <div className={`analysis-folder ${isExpanded ? 'expanded' : ''}`}>
            <div className="folder-header" onClick={toggleExpanded}>
                <div className="folder-structure">
                    <span className="folder-line">├─</span>
                    <span className="folder-icon">{isExpanded ? '📂' : '📁'}</span>
                    <div className="folder-info">
                        <div className="folder-name">
                            Analysis_{analysis.id}_{formatDate(analysis.created_at).replace(/[/\\s:,]/g, '_')}
                        </div>
                        <div className="folder-meta">
                            <span className="file-count">2 files</span>
                            <span className="separator">•</span>
                            <span className={`match-score ${getScoreColor(analysis.match_score)}`}>
                                {analysis.match_score}% match
                            </span>
                            <span className="separator">•</span>
                            <span className="date">{formatDate(analysis.created_at)}</span>
                        </div>
                    </div>
                </div>
                <div className="folder-actions">
                    <button
                        className="view-button"
                        onClick={(e) => {
                            e.stopPropagation();
                            onView(analysis.id);
                        }}
                        title="View detailed analysis"
                    >
                        👁️ View
                    </button>
                    <button
                        className="delete-button"
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(analysis.id);
                        }}
                        title="Delete analysis"
                    >
                        🗑️
                    </button>
                </div>
            </div>
            
            {isExpanded && (
                <div className="folder-contents">
                    <div className="file-entry">
                        <span className="file-line">│  ├─</span>
                        <span className="file-icon">📄</span>
                        <div className="file-details">
                            <span className="file-name">resume.pdf</span>
                            <span className="file-preview">
                                {analysis.resume_preview || 'Resume content preview...'}
                            </span>
                        </div>
                    </div>
                    <div className="file-entry">
                        <span className="file-line">│  ├─</span>
                        <span className="file-icon">📋</span>
                        <div className="file-details">
                            <span className="file-name">job_description.pdf</span>
                            <span className="file-preview">
                                {analysis.job_preview || 'Job description preview...'}
                            </span>
                        </div>
                    </div>
                    <div className="file-entry">
                        <span className="file-line">│  └─</span>
                        <span className="file-icon">📊</span>
                        <div className="file-details">
                            <span className="file-name">analysis_results.json</span>
                            <span className="file-preview">
                                Match score: {analysis.match_score}% • Created: {formatDate(analysis.created_at)}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const AnalysisHistory = ({ user }) => {
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sortBy, setSortBy] = useState('date');
    const [filterBy, setFilterBy] = useState('all');
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
        if (window.confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
            try {
                await axios.delete(`/api/analysis/${analysisId}`);
                setAnalyses(analyses.filter(analysis => analysis.id !== analysisId));
            } catch (error) {
                console.error('Error deleting analysis:', error);
                alert('Failed to delete analysis. Please try again.');
            }
        }
    };

    const getFilteredAndSortedAnalyses = () => {
        let filtered = [...analyses];

        // Apply filters
        if (filterBy !== 'all') {
            filtered = filtered.filter(analysis => {
                switch (filterBy) {
                    case 'excellent':
                        return analysis.match_score >= 80;
                    case 'good':
                        return analysis.match_score >= 60 && analysis.match_score < 80;
                    case 'fair':
                        return analysis.match_score >= 40 && analysis.match_score < 60;
                    case 'poor':
                        return analysis.match_score < 40;
                    default:
                        return true;
                }
            });
        }

        // Apply sorting
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'date':
                    return new Date(b.created_at) - new Date(a.created_at);
                case 'score-high':
                    return b.match_score - a.match_score;
                case 'score-low':
                    return a.match_score - b.match_score;
                default:
                    return 0;
            }
        });

        return filtered;
    };

    const filteredAnalyses = getFilteredAndSortedAnalyses();

    if (loading) {
        return (
            <div className="analysis-history">
                <div className="page-header">
                    <h1>📁 Analysis History</h1>
                    <p>Your comprehensive skill analysis archive</p>
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
            <div className="analysis-history">
                <div className="page-header">
                    <h1>📁 Analysis History</h1>
                    <p>Your comprehensive skill analysis archive</p>
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
        <div className="analysis-history">
            <div className="page-header">
                <h1>📁 Analysis History</h1>
                <p>Your comprehensive skill analysis archive - organized like a file system</p>
                <div className="history-stats">
                    <span className="stat">📊 Total: {analyses.length} analyses</span>
                    <span className="stat">
                        📈 Avg Score: {analyses.length > 0 ? Math.round(analyses.reduce((sum, a) => sum + a.match_score, 0) / analyses.length) : 0}%
                    </span>
                    <span className="stat">
                        🏆 Best: {analyses.length > 0 ? Math.max(...analyses.map(a => a.match_score)) : 0}%
                    </span>
                </div>
            </div>

            {analyses.length === 0 ? (
                <div className="empty-history">
                    <div className="empty-icon">📂</div>
                    <h3>No analysis history yet</h3>
                    <p>Start by creating your first skill analysis to build your portfolio!</p>
                    <button 
                        className="primary-button"
                        onClick={() => navigate('/match')}
                    >
                        🎯 Create First Analysis
                    </button>
                </div>
            ) : (
                <>
                    <div className="history-controls">
                        <div className="sort-controls">
                            <label>Sort by:</label>
                            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                                <option value="date">Date (Newest First)</option>
                                <option value="score-high">Score (Highest First)</option>
                                <option value="score-low">Score (Lowest First)</option>
                            </select>
                        </div>
                        <div className="filter-controls">
                            <label>Filter by Score:</label>
                            <select value={filterBy} onChange={(e) => setFilterBy(e.target.value)}>
                                <option value="all">All Scores</option>
                                <option value="excellent">Excellent (80%+)</option>
                                <option value="good">Good (60-79%)</option>
                                <option value="fair">Fair (40-59%)</option>
                                <option value="poor">Needs Improvement (&lt;40%)</option>
                            </select>
                        </div>
                    </div>

                    <div className="directory-view">
                        <div className="directory-header">
                            <span className="folder-icon">📁</span>
                            <span className="directory-path">~/SkillMatcher/User_{user.email.split('@')[0]}/Analyses/</span>
                            <span className="results-count">({filteredAnalyses.length} results)</span>
                        </div>
                        
                        <div className="folder-contents">
                            {filteredAnalyses.map((analysis) => (
                                <AnalysisFolder
                                    key={analysis.id}
                                    analysis={analysis}
                                    onView={handleViewAnalysis}
                                    onDelete={handleDeleteAnalysis}
                                />
                            ))}
                        </div>
                        
                        <div className="directory-footer">
                            <span className="folder-line">└─</span>
                            <span className="summary">
                                {filteredAnalyses.length} analysis folder{filteredAnalyses.length !== 1 ? 's' : ''} 
                                {filterBy !== 'all' && ` (filtered by ${filterBy})`}
                            </span>
                        </div>
                    </div>
                </>
            )}

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
                <button 
                    className="secondary-button"
                    onClick={() => navigate('/account')}
                >
                    👤 Account
                </button>
            </div>
        </div>
    );
};

export default AnalysisHistory;