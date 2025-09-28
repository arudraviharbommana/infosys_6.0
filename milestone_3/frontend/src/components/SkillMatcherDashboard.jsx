// src/components/SkillMatcherDashboard.jsx
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ThreeDScene from './ThreeDScene.jsx';
import ComprehensiveAnalysisResults from './ComprehensiveAnalysisResults.jsx';

const SkillMatcherDashboard = ({ user, onLogout }) => {
    const navigate = useNavigate();
    const [resumeText, setResumeText] = useState('');
    const [jdText, setJdText] = useState('');
    const [resumeFile, setResumeFile] = useState(null);
    const [jobFile, setJobFile] = useState(null);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('input');
    const [extractionStatus, setExtractionStatus] = useState({ resume: '', job: '' });
    const [analysisId, setAnalysisId] = useState(null);
    const [ollamaStatus, setOllamaStatus] = useState('checking');
    const [comprehensiveResults, setComprehensiveResults] = useState(null);
    const [showComprehensiveModal, setShowComprehensiveModal] = useState(false);
    const [isComprehensiveLoading, setIsComprehensiveLoading] = useState(false);
    const sceneContainerRef = useRef(null);

    // Sample data for demo
    const sampleResume = `Senior Software Engineer with 5+ years of experience in full-stack development. 
Proficient in Python, JavaScript, React, Node.js, and AWS. 
Experience with Docker, Kubernetes, and microservices architecture.
Strong background in machine learning and data analysis using pandas, numpy, and scikit-learn.
Led teams of 3-5 developers and managed CI/CD pipelines with Jenkins.`;

    const sampleJobDescription = `We are looking for a Senior Full-Stack Developer with 4+ years of experience.
Required skills: JavaScript, React, Node.js, Python, AWS, Docker.
Experience with machine learning and data science is a plus.
Must have experience with agile development and team leadership.
Knowledge of PostgreSQL and MongoDB preferred.`;

    // Check Ollama status on component mount
    React.useEffect(() => {
        const checkOllamaStatus = async () => {
            try {
                const response = await axios.get('/api/analysis/ollama-status');
                setOllamaStatus(response.data.status);
            } catch (error) {
                console.error('Error checking Ollama status:', error);
                setOllamaStatus('unavailable');
            }
        };
        checkOllamaStatus();
    }, []);

    const loadSampleData = () => {
        setResumeText(sampleResume);
        setJdText(sampleJobDescription);
    };

    const clearData = () => {
        setResumeText('');
        setJdText('');
        setResumeFile(null);
        setJobFile(null);
        setResults(null);
        setActiveTab('input');
        setExtractionStatus({ resume: '', job: '' });
        
        // Clear file inputs
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => input.value = '');
    };

    const handleLogout = () => {
        onLogout();
    };

    const handleMatch = async () => {
        if (!resumeText.trim() && !resumeFile) {
            alert('Please provide resume text or upload a resume file.');
            return;
        }

        if (!jdText.trim() && !jobFile) {
            alert('Please provide job description text or upload a job description file.');
            return;
        }

        setIsLoading(true);
        setResults(null);
        setActiveTab('results');

        try {
            let response;
            
            // If we have files, use FormData for multipart upload
            if (resumeFile || jobFile) {
                const formData = new FormData();
                
                if (resumeFile) {
                    formData.append('resume_file', resumeFile);
                }
                if (jobFile) {
                    formData.append('job_file', jobFile);
                }
                
                // Also append text data if available
                if (resumeText.trim()) {
                    formData.append('resumeText', resumeText.trim());
                }
                if (jdText.trim()) {
                    formData.append('jobDescription', jdText.trim());
                }

                response = await axios.post('/api/match', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else {
                // Use JSON for text-only requests
                response = await axios.post('/api/match', { 
                    resumeText: resumeText.trim(), 
                    jobDescription: jdText.trim() 
                });
            }

            setResults(response.data);
            // Store analysis ID for navigation
            if (response.data.id) {
                setAnalysisId(response.data.id);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            alert(error.response?.data?.error || 'Failed to connect to the server. Please make sure the backend is running.');
            setActiveTab('input');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = async (e, type) => {
        const file = e.target.files[0];
        if (!file) return;

        const allowedTypes = ['.txt', '.pdf'];
        const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
        
        if (!allowedTypes.includes(fileExtension)) {
            alert('Please upload a .txt or .pdf file');
            e.target.value = '';
            return;
        }

        if (type === 'resume') {
            setResumeFile(file);
            setExtractionStatus(prev => ({ ...prev, resume: 'Extracting...' }));
        } else {
            setJobFile(file);
            setExtractionStatus(prev => ({ ...prev, job: 'Extracting...' }));
        }

        if (fileExtension === '.txt') {
            // Handle text files
            const reader = new FileReader();
            reader.onload = (event) => {
                const text = event.target.result;
                if (type === 'resume') {
                    setResumeText(text);
                    setExtractionStatus(prev => ({ ...prev, resume: `✓ Extracted ${text.length} characters` }));
                } else {
                    setJdText(text);
                    setExtractionStatus(prev => ({ ...prev, job: `✓ Extracted ${text.length} characters` }));
                }
            };
            reader.readAsText(file);
        } else if (fileExtension === '.pdf') {
            // Handle PDF files
            // For PDF files, we'll let the backend handle extraction during analysis
            // Just set a status message for now
            if (type === 'resume') {
                setExtractionStatus(prev => ({ 
                    ...prev, 
                    resume: `✓ PDF file ready for analysis: ${file.name}` 
                }));
            } else {
                setExtractionStatus(prev => ({ 
                    ...prev, 
                    job: `✓ PDF file ready for analysis: ${file.name}` 
                }));
            }
        }
    };

    const getScoreColor = (score) => {
        if (score >= 80) return '#4caf50'; // Green
        if (score >= 60) return '#ff9800'; // Orange
        return '#f44336'; // Red
    };

    const getScoreLabel = (score) => {
        if (score >= 80) return 'Excellent Match';
        if (score >= 60) return 'Good Match';
        if (score >= 40) return 'Fair Match';
        return 'Poor Match';
    };

    const handleComprehensiveAnalysis = async () => {
        if (!resumeText.trim() && !resumeFile) {
            alert('Please provide resume text or upload a resume file for comprehensive analysis.');
            return;
        }

        setIsComprehensiveLoading(true);
        setComprehensiveResults(null);

        try {
            let response;
            
            if (resumeFile) {
                const formData = new FormData();
                formData.append('resume_file', resumeFile);
                
                if (resumeText.trim()) {
                    formData.append('resumeText', resumeText.trim());
                }
                if (jdText.trim()) {
                    formData.append('jobDescription', jdText.trim());
                }
                if (jobFile) {
                    formData.append('job_file', jobFile);
                }

                response = await axios.post('/api/analysis/comprehensive-analyze', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else {
                response = await axios.post('/api/analysis/comprehensive-analyze', { 
                    resumeText: resumeText.trim(),
                    jobDescription: jdText.trim()
                });
            }

            setComprehensiveResults(response.data);
            setShowComprehensiveModal(true);
        } catch (error) {
            console.error('Error performing comprehensive analysis:', error);
            alert(error.response?.data?.error || 'Failed to perform comprehensive analysis. Please try again.');
        } finally {
            setIsComprehensiveLoading(false);
        }
    };

    const handleQualityCheck = async () => {
        if (!resumeText.trim() && !resumeFile) {
            alert('Please provide resume text or upload a resume file for quality analysis.');
            return;
        }

        setIsComprehensiveLoading(true);

        try {
            let response;
            
            if (resumeFile) {
                const formData = new FormData();
                formData.append('resume_file', resumeFile);
                
                if (resumeText.trim()) {
                    formData.append('resumeText', resumeText.trim());
                }

                response = await axios.post('/api/analysis/quality-check', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                    },
                });
            } else {
                response = await axios.post('/api/analysis/quality-check', { 
                    resumeText: resumeText.trim()
                });
            }

            // Display quality results in comprehensive modal format
            const qualityData = {
                comprehensive_analysis: {
                    quality_analysis: response.data
                },
                summary: {
                    overall_quality: response.data.quality_assessment?.overall_score || 0,
                    total_skills_found: 'N/A',
                    career_level: 'Resume Quality Analysis'
                }
            };
            
            setComprehensiveResults(qualityData);
            setShowComprehensiveModal(true);
        } catch (error) {
            console.error('Error performing quality check:', error);
            alert(error.response?.data?.error || 'Failed to perform quality analysis. Please try again.');
        } finally {
            setIsComprehensiveLoading(false);
        }
    };

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <div className="header-content">
                    <h1>AI-Free Skill Matcher</h1>
                    <p>Advanced rule-based skill matching and analysis</p>
                </div>
                <div className="header-actions">
                    <button 
                        className="nav-button" 
                        onClick={() => navigate('/dashboard')}
                        title="Go to Dashboard"
                    >
                        📊 Dashboard
                    </button>
                    <button className="logout-button" onClick={handleLogout}>
                        Logout
                    </button>
                </div>
            </div>

            <div ref={sceneContainerRef} className="scene-container">
                <ThreeDScene />
            </div>
            
            <div className="dashboard-tabs">
                <button 
                    className={`tab-button ${activeTab === 'input' ? 'active' : ''}`}
                    onClick={() => setActiveTab('input')}
                >
                    Input & Analysis
                </button>
                <button 
                    className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
                    onClick={() => setActiveTab('results')}
                    disabled={!results && !isLoading}
                >
                    Results & Recommendations
                </button>
            </div>

            {activeTab === 'input' && (
                <div className="input-section">
                    <div className="section-header">
                        <h2>Input Your Data</h2>
                        <div className="action-buttons">
                            <button className="secondary-button" onClick={loadSampleData}>
                                Load Sample Data
                            </button>
                            <button className="secondary-button" onClick={clearData}>
                                Clear All
                            </button>
                        </div>
                    </div>

                    <div className="input-grid">
                        <div className="input-group">
                            <div className="input-header">
                                <label>Resume</label>
                                <div className="file-upload-section">
                                    <input
                                        type="file"
                                        accept=".txt,.pdf"
                                        onChange={(e) => handleFileUpload(e, 'resume')}
                                        className="file-input"
                                        id="resume-file"
                                    />
                                    <label htmlFor="resume-file" className="file-input-label">
                                        📄 Upload PDF/TXT
                                    </label>
                                </div>
                            </div>
                            {resumeFile && (
                                <div className="file-info">
                                    <span className="file-name">📎 {resumeFile.name}</span>
                                    <button 
                                        type="button" 
                                        className="remove-file"
                                        onClick={() => {
                                            setResumeFile(null);
                                            setExtractionStatus(prev => ({ ...prev, resume: '' }));
                                            document.getElementById('resume-file').value = '';
                                        }}
                                    >
                                        ✕
                                    </button>
                                </div>
                            )}
                            {extractionStatus.resume && (
                                <div className="extraction-status">
                                    {extractionStatus.resume}
                                </div>
                            )}
                            <textarea
                                value={resumeText}
                                onChange={(e) => setResumeText(e.target.value)}
                                placeholder="Paste your resume text here, or upload a PDF/TXT file above..."
                                rows="12"
                                className="large-textarea"
                            />
                            <div className="char-count">
                                {resumeText.length} characters
                                {resumeFile && ` • File: ${resumeFile.name}`}
                            </div>
                        </div>

                        <div className="input-group">
                            <div className="input-header">
                                <label>Job Description</label>
                                <div className="file-upload-section">
                                    <input
                                        type="file"
                                        accept=".txt,.pdf"
                                        onChange={(e) => handleFileUpload(e, 'job')}
                                        className="file-input"
                                        id="job-file"
                                    />
                                    <label htmlFor="job-file" className="file-input-label">
                                        📄 Upload PDF/TXT
                                    </label>
                                </div>
                            </div>
                            {jobFile && (
                                <div className="file-info">
                                    <span className="file-name">📎 {jobFile.name}</span>
                                    <button 
                                        type="button" 
                                        className="remove-file"
                                        onClick={() => {
                                            setJobFile(null);
                                            setExtractionStatus(prev => ({ ...prev, job: '' }));
                                            document.getElementById('job-file').value = '';
                                        }}
                                    >
                                        ✕
                                    </button>
                                </div>
                            )}
                            {extractionStatus.job && (
                                <div className="extraction-status">
                                    {extractionStatus.job}
                                </div>
                            )}
                            <textarea
                                value={jdText}
                                onChange={(e) => setJdText(e.target.value)}
                                placeholder="Paste the job description text here, or upload a PDF/TXT file above..."
                                rows="12"
                                className="large-textarea"
                            />
                            <div className="char-count">
                                {jdText.length} characters
                                {jobFile && ` • File: ${jobFile.name}`}
                            </div>
                        </div>
                    </div>

                    {/* Ollama Status Indicator */}
                    <div className="ollama-status-container">
                        <div className={`ollama-status ${ollamaStatus}`}>
                            {ollamaStatus === 'available' && (
                                <>
                                    🤖 <strong>Ollama AI Available</strong> - Advanced semantic analysis enabled
                                </>
                            )}
                            {ollamaStatus === 'unavailable' && (
                                <>
                                    ⚠️ <strong>Ollama AI Unavailable</strong> - Using standard analysis only
                                </>
                            )}
                            {ollamaStatus === 'checking' && (
                                <>
                                    🔄 <strong>Checking Ollama Status...</strong>
                                </>
                            )}
                        </div>
                    </div>

                    <div className="analysis-buttons-container">
                        <div className="primary-analysis-row">
                            <button 
                                className="match-button" 
                                onClick={handleMatch} 
                                disabled={isLoading || isComprehensiveLoading || (!resumeText.trim() && !resumeFile) || (!jdText.trim() && !jobFile)}
                            >
                                {isLoading ? (
                                    <>
                                        <span className="spinner"></span>
                                        Analyzing Skills...
                                    </>
                                ) : (
                                    '📊 Quick Analysis & Match'
                                )}
                            </button>

                            {ollamaStatus === 'available' && (
                                <button 
                                    className="comprehensive-button" 
                                    onClick={handleComprehensiveAnalysis} 
                                    disabled={isLoading || isComprehensiveLoading || (!resumeText.trim() && !resumeFile)}
                                    title="Advanced semantic analysis with career insights using Ollama AI"
                                >
                                    {isComprehensiveLoading ? (
                                        <>
                                            <span className="spinner"></span>
                                            AI Processing...
                                        </>
                                    ) : (
                                        '🤖 Comprehensive AI Analysis'
                                    )}
                                </button>
                            )}
                        </div>

                        <div className="secondary-analysis-row">
                            {ollamaStatus === 'available' && (
                                <button 
                                    className="quality-check-button" 
                                    onClick={handleQualityCheck} 
                                    disabled={isLoading || isComprehensiveLoading || (!resumeText.trim() && !resumeFile)}
                                    title="AI-powered resume quality assessment and improvement suggestions"
                                >
                                    {isComprehensiveLoading ? (
                                        <>
                                            <span className="spinner"></span>
                                            Checking...
                                        </>
                                    ) : (
                                        '✨ Resume Quality Check'
                                    )}
                                </button>
                            )}
                            
                            <div className="analysis-info">
                                <span className="info-text">
                                    💡 Tip: {ollamaStatus === 'available' 
                                        ? 'Try Comprehensive Analysis for detailed career insights and personalized recommendations!'
                                        : 'Enable Ollama for advanced AI analysis features!'
                                    }
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === 'results' && (
                <div className="results-section">
                    {isLoading ? (
                        <div className="loading-container">
                            <div className="loading-spinner"></div>
                            <h3>Analyzing your skills...</h3>
                            <p>This may take a few moments</p>
                        </div>
                    ) : results ? (
                        <>
                            <div className="results-header">
                                <h2>Match Analysis Results</h2>
                                <div className="overall-score" style={{ color: getScoreColor(results.match_summary.overall_score) }}>
                                    <div className="score-number">
                                        {results.match_summary.overall_score}%
                                    </div>
                                    <div className="score-label">
                                        {getScoreLabel(results.match_summary.overall_score)}
                                    </div>
                                </div>
                            </div>

                            <div className="results-grid">
                                <div className="result-card">
                                    <h3>Detailed Scores</h3>
                                    <div className="score-grid">
                                        {Object.entries(results.match_summary.detailed_scores).map(([key, value]) => (
                                            <div key={key} className="score-item">
                                                <span className="score-name">
                                                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                </span>
                                                <span className="score-value" style={{ color: getScoreColor(value) }}>
                                                    {value}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="result-card">
                                    <h3>Skills Breakdown</h3>
                                    <div className="skills-summary">
                                        <div className="skill-stat">
                                            <span className="stat-number matched">{results.skills_analysis.matched_skills.length}</span>
                                            <span className="stat-label">Matched Skills</span>
                                        </div>
                                        <div className="skill-stat">
                                            <span className="stat-number missing">{results.skills_analysis.missing_skills.length}</span>
                                            <span className="stat-label">Missing Skills</span>
                                        </div>
                                        <div className="skill-stat">
                                            <span className="stat-number extra">{results.skills_analysis.extra_skills.length}</span>
                                            <span className="stat-label">Extra Skills</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="detailed-results">
                                {/* SKILLS MATCHING SUMMARY TABLE */}
                                {results.comparison && results.comparison.length > 0 && (
                                    <div className="result-card">
                                        <h3>Skills Matching Summary</h3>
                                        <div className="table-wrapper">
                                            <table className="skills-table">
                                                <thead>
                                                    <tr>
                                                        <th>Your Skill</th>
                                                        <th>Job Requirement</th>
                                                        <th>Match Type</th>
                                                        <th>Similarity</th>
                                                        <th>Category</th>
                                                        <th>Priority</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {results.comparison.map((match, index) => (
                                                        <tr key={index} className={`skill-row ${match.matchType?.toLowerCase().replace(' ', '-') || 'default'}`}>
                                                            <td data-label="Your Skill">{match.resumeSkill || 'N/A'}</td>
                                                            <td data-label="Job Requirement">{match.jobSkill || 'N/A'}</td>
                                                            <td data-label="Match Type">
                                                                <span className={`match-badge ${match.matchType?.toLowerCase().replace(' ', '-') || 'default'}`}>
                                                                    {match.matchType || 'UNKNOWN'}
                                                                </span>
                                                            </td>
                                                            <td data-label="Similarity">
                                                                <div className="similarity-bar-container">
                                                                    <div 
                                                                        className="similarity-bar" 
                                                                        style={{
                                                                            width: `${(match.similarityScore || 0) * 100}%`,
                                                                            backgroundColor: getScoreColor((match.similarityScore || 0) * 100)
                                                                        }}
                                                                    >
                                                                        <span>{Math.round((match.similarityScore || 0) * 100)}%</span>
                                                                    </div>
                                                                </div>
                                                            </td>
                                                            <td data-label="Category">{match.category || 'N/A'}</td>
                                                            <td data-label="Priority">
                                                                <span className={`priority-badge ${match.priority?.toLowerCase() || 'default'}`}>
                                                                    {match.priority || 'N/A'}
                                                                </span>
                                                            </td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )}

                                <div className="result-section">
                                    <h3>Matched Skills</h3>
                                    <div className="skills-list matched-skills">
                                        {results.skills_analysis.matched_skills.map((skill, index) => (
                                            <span key={index} className="skill-tag matched">{skill}</span>
                                        ))}
                                        {results.skills_analysis.matched_skills.length === 0 && (
                                            <p className="no-skills">No matched skills found</p>
                                        )}
                                    </div>
                                </div>

                                <div className="result-section">
                                    <h3>Additional Skills (Your Advantages)</h3>
                                    <div className="skills-list extra-skills">
                                        {results.skills_analysis.extra_skills.map((skill, index) => (
                                            <span key={index} className="skill-tag extra">{skill}</span>
                                        ))}
                                        {results.skills_analysis.extra_skills.length === 0 && (
                                            <p className="no-skills">No additional skills found</p>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* LEARNING RECOMMENDATIONS */}
                            {results.learning_path_recommendations && results.learning_path_recommendations.length > 0 && (
                                <div className="result-card">
                                    <h3>Learning Path Recommendations</h3>
                                    <p className="recommendation-intro">Focus on these skills to better match the job requirements.</p>
                                    <div className="skills-list missing-skills">
                                        {results.learning_path_recommendations.map((rec, index) => (
                                            <div key={index} className="recommendation-card">
                                                <div className="recommendation-header">
                                                    <span className="skill-tag missing">{rec.skill}</span>
                                                    <span className={`priority-badge ${rec.priority?.toLowerCase() || 'default'}`}>{rec.priority || 'Medium'} Priority</span>
                                                </div>
                                                <p className="recommendation-reason">{rec.reason}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Navigation Actions */}
                            <div className="result-actions">
                                <div className="action-group">
                                    <button 
                                        className="primary-button"
                                        onClick={() => navigate('/dashboard')}
                                    >
                                        📊 View Dashboard
                                    </button>
                                    {analysisId && (
                                        <button 
                                            className="secondary-button"
                                            onClick={() => navigate(`/result/${analysisId}`)}
                                        >
                                            📋 Detailed View
                                        </button>
                                    )}
                                    <button 
                                        className="secondary-button"
                                        onClick={() => navigate('/history')}
                                    >
                                        📚 View History
                                    </button>
                                </div>
                                <div className="action-group">
                                    <button 
                                        className="tertiary-button"
                                        onClick={() => {
                                            setActiveTab('input');
                                            setResults(null);
                                            setAnalysisId(null);
                                        }}
                                    >
                                        🔄 New Analysis
                                    </button>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="no-results">
                            <h3>No results yet</h3>
                            <p>Please go to the Input tab and analyze your resume against a job description.</p>
                            <button 
                                className="secondary-button" 
                                onClick={() => setActiveTab('input')}
                            >
                                Go to Input
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Comprehensive Analysis Modal */}
            {showComprehensiveModal && comprehensiveResults && (
                <ComprehensiveAnalysisResults
                    analysisData={comprehensiveResults}
                    onClose={() => {
                        setShowComprehensiveModal(false);
                        setComprehensiveResults(null);
                    }}
                />
            )}
        </div>
    );
};

export default SkillMatcherDashboard;