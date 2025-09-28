import React, { useState, useEffect } from 'react';

const ComprehensiveAnalysisResults = ({ analysisData, onClose }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [expandedSections, setExpandedSections] = useState({});

    const toggleSection = (sectionId) => {
        setExpandedSections(prev => ({
            ...prev,
            [sectionId]: !prev[sectionId]
        }));
    };

    const renderSkillProficiency = (skillProficiency) => {
        return (
            <div className="skill-proficiency-grid">
                {Object.entries(skillProficiency || {}).map(([skill, data]) => (
                    <div key={skill} className="skill-proficiency-card">
                        <div className="skill-name">{skill}</div>
                        <div className="proficiency-details">
                            <div className={`proficiency-level level-${data.level}`}>
                                {data.level}
                            </div>
                            <div className="confidence-score">
                                Confidence: {Math.round((data.confidence || 0) * 100)}%
                            </div>
                            {data.years_experience && (
                                <div className="experience-years">
                                    Experience: {data.years_experience}
                                </div>
                            )}
                            {data.evidence && data.evidence.length > 0 && (
                                <div className="evidence-list">
                                    <strong>Evidence:</strong>
                                    <ul>
                                        {data.evidence.slice(0, 2).map((evidence, idx) => (
                                            <li key={idx}>{evidence}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    const renderSemanticInsights = (insights) => {
        return (
            <div className="semantic-insights">
                <div className="insights-grid">
                    <div className="insight-card">
                        <h4>Career Level</h4>
                        <div className={`career-level level-${insights.career_level}`}>
                            {insights.career_level}
                        </div>
                    </div>
                    <div className="insight-card">
                        <h4>Primary Domain</h4>
                        <div className="primary-domain">{insights.primary_domain}</div>
                    </div>
                    <div className="insight-card">
                        <h4>Experience Years</h4>
                        <div className="experience-estimate">{insights.experience_years || 'Not specified'}</div>
                    </div>
                </div>

                <div className="insight-section">
                    <h4>Strongest Skills</h4>
                    <div className="skill-tags">
                        {(insights.strongest_skills || []).map((skill, idx) => (
                            <span key={idx} className="skill-tag strong">{skill}</span>
                        ))}
                    </div>
                </div>

                <div className="insight-section">
                    <h4>Emerging Skills</h4>
                    <div className="skill-tags">
                        {(insights.emerging_skills || []).map((skill, idx) => (
                            <span key={idx} className="skill-tag emerging">{skill}</span>
                        ))}
                    </div>
                </div>

                <div className="insight-section">
                    <h4>Career Trajectory</h4>
                    <p className="trajectory-analysis">{insights.career_trajectory}</p>
                </div>

                {insights.unique_strengths && insights.unique_strengths.length > 0 && (
                    <div className="insight-section">
                        <h4>Unique Strengths</h4>
                        <ul className="strengths-list">
                            {insights.unique_strengths.map((strength, idx) => (
                                <li key={idx}>{strength}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        );
    };

    const renderJobMatching = (matching) => {
        return (
            <div className="job-matching-analysis">
                <div className="match-summary">
                    <div className="match-score-display">
                        <div className={`match-score-circle score-${Math.floor(matching.match_analysis?.overall_match_score / 25)}`}>
                            <span className="score-value">{matching.match_analysis?.overall_match_score}%</span>
                            <span className="score-label">Match</span>
                        </div>
                        <div className="match-confidence">
                            Confidence: {matching.match_analysis?.confidence_level}
                        </div>
                    </div>
                    <div className="match-summary-text">
                        <p>{matching.match_analysis?.match_summary}</p>
                    </div>
                </div>

                <div className="matching-sections">
                    <div className="matching-section">
                        <h4>✅ Perfect Matches</h4>
                        <div className="skill-matches">
                            {(matching.detailed_skill_comparison?.perfectly_matched || []).map((match, idx) => (
                                <div key={idx} className="skill-match-card perfect">
                                    <div className="skill-name">{match.skill}</div>
                                    <div className="match-details">
                                        <div className="resume-evidence">
                                            <strong>Resume:</strong> {match.resume_evidence}
                                        </div>
                                        <div className="job-requirement">
                                            <strong>Job:</strong> {match.job_requirement}
                                        </div>
                                        <div className={`strength-level ${match.strength_level}`}>
                                            {match.strength_level} match
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="matching-section">
                        <h4>⚠️ Partial Matches</h4>
                        <div className="skill-matches">
                            {(matching.detailed_skill_comparison?.partially_matched || []).map((match, idx) => (
                                <div key={idx} className="skill-match-card partial">
                                    <div className="skill-name">{match.skill}</div>
                                    <div className="match-details">
                                        <div className="candidate-skill">
                                            <strong>You have:</strong> {match.resume_skill}
                                        </div>
                                        <div className="job-needs">
                                            <strong>Job needs:</strong> {match.job_requirement}
                                        </div>
                                        <div className="gap-analysis">
                                            <strong>Gap:</strong> {match.gap_analysis}
                                        </div>
                                        <div className={`bridgeability ${match.bridgeability}`}>
                                            Bridge difficulty: {match.bridgeability}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="matching-section">
                        <h4>❌ Missing Skills</h4>
                        <div className="skill-matches">
                            {(matching.detailed_skill_comparison?.missing_skills || []).map((missing, idx) => (
                                <div key={idx} className="skill-match-card missing">
                                    <div className="skill-name">{missing.skill}</div>
                                    <div className="match-details">
                                        <div className={`importance ${missing.importance}`}>
                                            Importance: {missing.importance}
                                        </div>
                                        <div className={`learning-effort ${missing.learning_effort}`}>
                                            Learning effort: {missing.learning_effort}
                                        </div>
                                        {missing.alternatives && missing.alternatives.length > 0 && (
                                            <div className="alternatives">
                                                <strong>Your alternatives:</strong> {missing.alternatives.join(', ')}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderCareerRecommendations = (recommendations) => {
        return (
            <div className="career-recommendations">
                <div className="recommendation-section">
                    <h4>🎯 Career Strategy</h4>
                    <div className="strategy-overview">
                        <p><strong>Current Position:</strong> {recommendations.career_strategy?.current_position_assessment}</p>
                        <p><strong>Market Positioning:</strong> {recommendations.career_strategy?.market_positioning}</p>
                    </div>
                    
                    <div className="competitive-advantages">
                        <h5>Competitive Advantages</h5>
                        <ul>
                            {(recommendations.career_strategy?.competitive_advantages || []).map((advantage, idx) => (
                                <li key={idx}>{advantage}</li>
                            ))}
                        </ul>
                    </div>
                </div>

                <div className="recommendation-section">
                    <h4>📈 Skill Development Roadmap</h4>
                    
                    <div className="roadmap-section">
                        <h5>Immediate Focus (Next 3 months)</h5>
                        {(recommendations.skill_development_roadmap?.immediate_focus || []).map((skill, idx) => (
                            <div key={idx} className="skill-development-card immediate">
                                <div className="skill-header">
                                    <span className="skill-name">{skill.skill}</span>
                                    <span className={`importance ${skill.importance}`}>{skill.importance}</span>
                                </div>
                                <div className="skill-details">
                                    <div className="timeline">⏱️ {skill.timeline}</div>
                                    <div className="resources">
                                        <strong>Resources:</strong> {skill.learning_resources?.join(', ')}
                                    </div>
                                    <div className="practice">
                                        <strong>Practice:</strong> {skill.practice_opportunities?.join(', ')}
                                    </div>
                                    <div className="success-metrics">
                                        <strong>Success metrics:</strong> {skill.success_metrics}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="roadmap-section">
                        <h5>Medium-term Goals (6-18 months)</h5>
                        {(recommendations.skill_development_roadmap?.medium_term_goals || []).map((goal, idx) => (
                            <div key={idx} className="skill-development-card medium-term">
                                <div className="goal-header">
                                    <span className="skill-cluster">{goal.skill_cluster}</span>
                                    <span className="target-proficiency">Target: {goal.target_proficiency}</span>
                                </div>
                                <div className="goal-details">
                                    <div className="timeline">⏱️ {goal.timeline}</div>
                                    <div className="learning-path">
                                        <strong>Path:</strong> {goal.learning_path?.join(' → ')}
                                    </div>
                                    <div className="career-impact">
                                        <strong>Impact:</strong> {goal.career_impact}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="recommendation-section">
                    <h4>🌐 Industry Insights</h4>
                    <div className="industry-insights">
                        <div className="trending-skills">
                            <h5>📈 Trending Skills</h5>
                            <div className="skill-tags">
                                {(recommendations.industry_insights?.trending_skills || []).map((skill, idx) => (
                                    <span key={idx} className="skill-tag trending">{skill}</span>
                                ))}
                            </div>
                        </div>
                        
                        <div className="salary-expectations">
                            <h5>💰 Salary Expectations</h5>
                            <div className="salary-info">
                                <p><strong>Current Range:</strong> {recommendations.industry_insights?.salary_expectations?.current_range}</p>
                                <p><strong>Growth Potential:</strong> {recommendations.industry_insights?.salary_expectations?.growth_potential}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="recommendation-section">
                    <h4>🎯 Job Search Strategy</h4>
                    <div className="job-search-strategy">
                        <div className="target-roles">
                            <h5>Target Roles</h5>
                            <div className="role-tags">
                                {(recommendations.job_search_strategy?.job_titles || []).map((title, idx) => (
                                    <span key={idx} className="role-tag">{title}</span>
                                ))}
                            </div>
                        </div>
                        
                        <div className="application-strategy">
                            <h5>Application Strategy</h5>
                            <ul>
                                {(recommendations.job_search_strategy?.application_strategy || []).map((strategy, idx) => (
                                    <li key={idx}>{strategy}</li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    const renderQualityAnalysis = (qualityData) => {
        const getScoreColor = (score) => {
            if (score >= 80) return 'excellent';
            if (score >= 60) return 'good';
            if (score >= 40) return 'fair';
            return 'poor';
        };

        return (
            <div className="quality-analysis">
                <div className="quality-scores">
                    <h4>Quality Scores</h4>
                    <div className="scores-grid">
                        <div className="score-card">
                            <div className={`score-value ${getScoreColor(qualityData.quality_assessment?.overall_score)}`}>
                                {qualityData.quality_assessment?.overall_score}%
                            </div>
                            <div className="score-label">Overall</div>
                        </div>
                        <div className="score-card">
                            <div className={`score-value ${getScoreColor(qualityData.quality_assessment?.readability_score)}`}>
                                {qualityData.quality_assessment?.readability_score}%
                            </div>
                            <div className="score-label">Readability</div>
                        </div>
                        <div className="score-card">
                            <div className={`score-value ${getScoreColor(qualityData.quality_assessment?.ats_compatibility)}`}>
                                {qualityData.quality_assessment?.ats_compatibility}%
                            </div>
                            <div className="score-label">ATS Compatible</div>
                        </div>
                        <div className="score-card">
                            <div className={`score-value ${getScoreColor(qualityData.quality_assessment?.impact_score)}`}>
                                {qualityData.quality_assessment?.impact_score}%
                            </div>
                            <div className="score-label">Impact</div>
                        </div>
                    </div>
                </div>

                <div className="improvement-recommendations">
                    <h4>Improvement Recommendations</h4>
                    
                    {qualityData.improvement_recommendations?.high_priority && (
                        <div className="priority-section high-priority">
                            <h5>🔴 High Priority</h5>
                            {qualityData.improvement_recommendations.high_priority.map((rec, idx) => (
                                <div key={idx} className="recommendation-card">
                                    <div className="issue">{rec.issue}</div>
                                    <div className="suggestion">{rec.suggestion}</div>
                                    {rec.example && <div className="example"><strong>Example:</strong> {rec.example}</div>}
                                    <div className="impact"><strong>Impact:</strong> {rec.impact}</div>
                                </div>
                            ))}
                        </div>
                    )}

                    {qualityData.improvement_recommendations?.medium_priority && (
                        <div className="priority-section medium-priority">
                            <h5>🟡 Medium Priority</h5>
                            {qualityData.improvement_recommendations.medium_priority.map((rec, idx) => (
                                <div key={idx} className="recommendation-card">
                                    <div className="issue">{rec.issue}</div>
                                    <div className="suggestion">{rec.suggestion}</div>
                                    <div className="impact">{rec.impact}</div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        );
    };

    if (!analysisData) {
        return <div className="loading">Loading comprehensive analysis...</div>;
    }

    return (
        <div className="comprehensive-analysis-modal">
            <div className="modal-overlay" onClick={onClose}>
                <div className="modal-content" onClick={e => e.stopPropagation()}>
                    <div className="modal-header">
                        <h2>🤖 Ollama-Enhanced Analysis Results</h2>
                        <button className="close-button" onClick={onClose}>×</button>
                    </div>

                    <div className="analysis-tabs">
                        <button 
                            className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                            onClick={() => setActiveTab('overview')}
                        >
                            📊 Overview
                        </button>
                        <button 
                            className={`tab ${activeTab === 'skills' ? 'active' : ''}`}
                            onClick={() => setActiveTab('skills')}
                        >
                            🎯 Skills
                        </button>
                        <button 
                            className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
                            onClick={() => setActiveTab('insights')}
                        >
                            🧠 Insights
                        </button>
                        {analysisData.comprehensive_analysis?.job_matching && (
                            <button 
                                className={`tab ${activeTab === 'matching' ? 'active' : ''}`}
                                onClick={() => setActiveTab('matching')}
                            >
                                🎪 Job Match
                            </button>
                        )}
                        {analysisData.comprehensive_analysis?.career_recommendations && (
                            <button 
                                className={`tab ${activeTab === 'recommendations' ? 'active' : ''}`}
                                onClick={() => setActiveTab('recommendations')}
                            >
                                🚀 Recommendations
                            </button>
                        )}
                        {analysisData.comprehensive_analysis?.quality_analysis && (
                            <button 
                                className={`tab ${activeTab === 'quality' ? 'active' : ''}`}
                                onClick={() => setActiveTab('quality')}
                            >
                                ✨ Quality
                            </button>
                        )}
                    </div>

                    <div className="tab-content">
                        {activeTab === 'overview' && (
                            <div className="overview-tab">
                                <div className="summary-cards">
                                    <div className="summary-card">
                                        <div className="summary-value">{analysisData.summary?.total_skills_found}</div>
                                        <div className="summary-label">Skills Found</div>
                                    </div>
                                    <div className="summary-card">
                                        <div className="summary-value">{analysisData.summary?.career_level}</div>
                                        <div className="summary-label">Career Level</div>
                                    </div>
                                    {analysisData.summary?.match_score && (
                                        <div className="summary-card">
                                            <div className="summary-value">{analysisData.summary.match_score}%</div>
                                            <div className="summary-label">Job Match</div>
                                        </div>
                                    )}
                                    <div className="summary-card">
                                        <div className="summary-value">{analysisData.summary?.overall_quality}%</div>
                                        <div className="summary-label">Resume Quality</div>
                                    </div>
                                </div>
                                
                                <div className="analysis-powered-by">
                                    <div className="powered-by-badge">
                                        🤖 Powered by Ollama AI - Advanced semantic analysis
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'skills' && analysisData.comprehensive_analysis?.skill_extraction && (
                            <div className="skills-tab">
                                {renderSkillProficiency(analysisData.comprehensive_analysis.skill_extraction.skill_proficiency)}
                            </div>
                        )}

                        {activeTab === 'insights' && analysisData.comprehensive_analysis?.skill_extraction && (
                            <div className="insights-tab">
                                {renderSemanticInsights(analysisData.comprehensive_analysis.skill_extraction.semantic_insights)}
                            </div>
                        )}

                        {activeTab === 'matching' && analysisData.comprehensive_analysis?.job_matching && (
                            <div className="matching-tab">
                                {renderJobMatching(analysisData.comprehensive_analysis.job_matching)}
                            </div>
                        )}

                        {activeTab === 'recommendations' && analysisData.comprehensive_analysis?.career_recommendations && (
                            <div className="recommendations-tab">
                                {renderCareerRecommendations(analysisData.comprehensive_analysis.career_recommendations)}
                            </div>
                        )}

                        {activeTab === 'quality' && analysisData.comprehensive_analysis?.quality_analysis && (
                            <div className="quality-tab">
                                {renderQualityAnalysis(analysisData.comprehensive_analysis.quality_analysis)}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ComprehensiveAnalysisResults;