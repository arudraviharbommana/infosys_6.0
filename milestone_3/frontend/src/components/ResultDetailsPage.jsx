import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const ResultDetailsPage = ({ user }) => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchAnalysisDetails = useCallback(async () => {
        try {
            const response = await axios.get(`/api/analysis/${id}`);
            setAnalysis(response.data);
        } catch (error) {
            setError('Failed to load analysis details');
            console.error('Error fetching analysis:', error);
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchAnalysisDetails();
    }, [fetchAnalysisDetails]);

    const getScoreColor = (score) => {
        if (score >= 80) return '#22c55e'; // green
        if (score >= 60) return '#eab308'; // yellow
        if (score >= 40) return '#f97316'; // orange
        return '#ef4444'; // red
    };

    const renderSkillsList = (skills, title, className = '') => {
        if (!skills || skills.length === 0) return null;
        
        return (
            <div className={`skills-section ${className}`}>
                <h4>{title} ({skills.length})</h4>
                <div className="skills-list">
                    {skills.map((skill, index) => (
                        <span key={index} className="skill-tag">
                            {skill}
                        </span>
                    ))}
                </div>
            </div>
        );
    };

    const renderStrengthAssessments = (assessments) => {
        if (!assessments || assessments.length === 0) return null;

        return (
            <div className="strength-assessments">
                <h3>Strength Assessments</h3>
                <div className="assessments-grid">
                    {assessments.map((assessment, index) => (
                        <div key={index} className="assessment-card">
                            <div className="assessment-header">
                                <h4>{assessment.category}</h4>
                                <div 
                                    className="assessment-score"
                                    style={{ color: getScoreColor(assessment.score) }}
                                >
                                    {assessment.score}%
                                </div>
                            </div>
                            <p className="assessment-description">
                                {assessment.description}
                            </p>
                            {assessment.recommendations && assessment.recommendations.length > 0 && (
                                <div className="assessment-recommendations">
                                    <strong>Recommendations:</strong>
                                    <ul>
                                        {assessment.recommendations.map((rec, idx) => (
                                            <li key={idx}>{rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div className="result-details-page">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading analysis details...</p>
                </div>
            </div>
        );
    }

    if (error || !analysis) {
        return (
            <div className="result-details-page">
                <div className="error-container">
                    <h2>Error</h2>
                    <p>{error || 'Analysis not found'}</p>
                    <button 
                        className="primary-button"
                        onClick={() => navigate('/dashboard')}
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    const { detailed_analysis, strength_assessments, match_score, created_at } = analysis;

    return (
        <div className="result-details-page">
            <div className="result-header">
                <div className="header-content">
                    <div className="back-navigation">
                        <button 
                            className="back-button"
                            onClick={() => navigate('/dashboard')}
                        >
                            ← Back to Dashboard
                        </button>
                    </div>
                    <h1>Analysis Results</h1>
                    <p>Detailed analysis from {new Date(created_at).toLocaleDateString()}</p>
                </div>
                <div className="overall-score">
                    <div 
                        className="score-circle-large"
                        style={{ color: getScoreColor(match_score) }}
                    >
                        {match_score}%
                    </div>
                    <span>Overall Match</span>
                </div>
            </div>

            <div className="result-content">
                {/* Match Summary */}
                <div className="result-section">
                    <h2>Match Summary</h2>
                    <div className="score-breakdown">
                        {Object.entries(detailed_analysis.match_summary.detailed_scores || {}).map(([category, score]) => (
                            <div key={category} className="score-item">
                                <span className="score-label">{category.replace(/_/g, ' ').toUpperCase()}</span>
                                <div className="score-bar">
                                    <div 
                                        className="score-fill"
                                        style={{ 
                                            width: `${score}%`,
                                            backgroundColor: getScoreColor(score)
                                        }}
                                    ></div>
                                </div>
                                <span className="score-value">{score}%</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Skills Analysis */}
                <div className="result-section">
                    <h2>Skills Analysis</h2>
                    <div className="skills-grid">
                        {renderSkillsList(
                            detailed_analysis.skills_analysis.matched_skills,
                            'Matched Skills',
                            'matched-skills'
                        )}
                        {renderSkillsList(
                            detailed_analysis.skills_analysis.missing_skills,
                            'Missing Skills',
                            'missing-skills'
                        )}
                        {renderSkillsList(
                            detailed_analysis.skills_analysis.extra_skills,
                            'Additional Skills',
                            'extra-skills'
                        )}
                    </div>
                </div>

                {/* Strength Assessments */}
                {renderStrengthAssessments(strength_assessments)}

                {/* Learning Recommendations */}
                {detailed_analysis.learning_path_recommendations && 
                 detailed_analysis.learning_path_recommendations.length > 0 && (
                    <div className="result-section">
                        <h2>Learning Recommendations</h2>
                        <div className="recommendations-list">
                            {detailed_analysis.learning_path_recommendations.map((rec, index) => (
                                <div key={index} className="recommendation-item">
                                    <h4>{rec.skill || rec.title || `Recommendation ${index + 1}`}</h4>
                                    <p>{rec.description || rec.suggestion || rec}</p>
                                    {rec.resources && rec.resources.length > 0 && (
                                        <div className="recommendation-resources">
                                            <strong>Resources:</strong>
                                            <ul>
                                                {rec.resources.map((resource, idx) => (
                                                    <li key={idx}>{resource}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Experience Analysis */}
                {detailed_analysis.experience_analysis && (
                    <div className="result-section">
                        <h2>Experience Analysis</h2>
                        <div className="experience-comparison">
                            <div className="experience-section">
                                <h4>Your Experience</h4>
                                <p>{detailed_analysis.experience_analysis.resume_experience || 'No experience data available'}</p>
                            </div>
                            <div className="experience-section">
                                <h4>Required Experience</h4>
                                <p>{detailed_analysis.experience_analysis.job_experience || 'No experience requirements specified'}</p>
                            </div>
                        </div>
                    </div>
                )}

                <div className="result-actions">
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
                        📊 View All Results
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ResultDetailsPage;