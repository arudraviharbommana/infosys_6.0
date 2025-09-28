import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Dashboard = ({ user }) => {
    const [analyses, setAnalyses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchAnalyses();
    }, []);

    const fetchAnalyses = async () => {
        try {
            const response = await axios.get('/api/analyses');
            setAnalyses(response.data.analyses);
        } catch (error) {
            setError('Failed to load analysis history');
            console.error('Error fetching analyses:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGetMatched = () => {
        navigate('/match');
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
        if (score >= 80) return '#22c55e'; // green
        if (score >= 60) return '#eab308'; // yellow
        if (score >= 40) return '#f97316'; // orange
        return '#ef4444'; // red
    };

    return (
        <div className="dashboard">
            <div className="dashboard-header">
                <h1>Welcome back, {user.email.split('@')[0]}!</h1>
                <p>Here's your skill analysis dashboard</p>
                
                <div className="quick-actions">
                    <button 
                        className="primary-button"
                        onClick={handleGetMatched}
                    >
                        🎯 Get Matched
                    </button>
                </div>
            </div>

            <div className="dashboard-content">
                <div className="stats-cards">
                    <div className="stat-card">
                        <h3>Total Analyses</h3>
                        <div className="stat-number">{analyses.length}</div>
                    </div>
                    <div className="stat-card">
                        <h3>Average Score</h3>
                        <div className="stat-number">
                            {analyses.length > 0 
                                ? Math.round(analyses.reduce((sum, a) => sum + a.match_score, 0) / analyses.length)
                                : 0
                            }%
                        </div>
                    </div>
                    <div className="stat-card">
                        <h3>Best Match</h3>
                        <div className="stat-number">
                            {analyses.length > 0 
                                ? Math.max(...analyses.map(a => a.match_score))
                                : 0
                            }%
                        </div>
                    </div>
                </div>

                <div className="analysis-history">
                    <div className="section-header">
                        <h2>Analysis History</h2>
                        <p>Your recent skill matching results</p>
                    </div>

                    {loading ? (
                        <div className="loading-spinner">Loading...</div>
                    ) : error ? (
                        <div className="error-message">{error}</div>
                    ) : analyses.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📊</div>
                            <h3>No analyses yet</h3>
                            <p>Start by running your first skill analysis</p>
                            <button 
                                className="primary-button"
                                onClick={handleGetMatched}
                            >
                                Create First Analysis
                            </button>
                        </div>
                    ) : (
                        <div className="analysis-list">
                            {analyses.map((analysis) => (
                                <div key={analysis.id} className="simple-analysis-row">
                                    <div className="analysis-info">
                                        <div className="file-names">
                                            <span className="resume-name">📄 Resume_{analysis.id}.pdf</span>
                                            <span className="separator">→</span>
                                            <span className="job-name">📋 JobDesc_{analysis.id}.pdf</span>
                                        </div>
                                        <div className="analysis-date">
                                            {formatDate(analysis.created_at)}
                                        </div>
                                    </div>
                                    <div className={`match-score-badge ${getScoreColor(analysis.match_score)}`}>
                                        {analysis.match_score}% Match
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;