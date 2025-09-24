// src/components/SkillMatcherDashboard.jsx
import React, { useState, useRef, useEffect } from 'react';
import ThreeDScene from './ThreeDScene.jsx';

const SkillMatcherDashboard = ({ setIsAuthenticated }) => {
    const [resumeText, setResumeText] = useState('');
    const [jdText, setJdText] = useState('');
    const [resumeFile, setResumeFile] = useState(null);
    const [jobFile, setJobFile] = useState(null);
    const [results, setResults] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('input');
    const [extractionStatus, setExtractionStatus] = useState({ resume: '', job: '' });
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
        setIsAuthenticated(false);
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

                response = await fetch('/api/match', {
                    method: 'POST',
                    body: formData,
                });
            } else {
                // Use JSON for text-only requests
                response = await fetch('/api/match', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        resumeText: resumeText.trim(), 
                        jobDescription: jdText.trim() 
                    }),
                });
            }

            const data = await response.json();
            
            if (response.ok) {
                setResults(data);
            } else {
                alert(data.error || 'Failed to process the request');
                setActiveTab('input');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            alert('Failed to connect to the server. Please make sure the backend is running.');
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
            try {
                const formData = new FormData();
                formData.append('pdf_file', file);

                const response = await fetch('/api/extract-pdf', {
                    method: 'POST',
                    body: formData,
                });

                const data = await response.json();
                
                if (response.ok) {
                    if (type === 'resume') {
                        setResumeText(data.extracted_text);
                        setExtractionStatus(prev => ({ 
                            ...prev, 
                            resume: `✓ PDF extracted: ${data.word_count} words, ${data.skills_found} skills found` 
                        }));
                    } else {
                        setJdText(data.extracted_text);
                        setExtractionStatus(prev => ({ 
                            ...prev, 
                            job: `✓ PDF extracted: ${data.word_count} words, ${data.skills_found} skills found` 
                        }));
                    }
                } else {
                    throw new Error(data.error || 'Failed to extract text from PDF');
                }
            } catch (error) {
                console.error('Error extracting PDF:', error);
                alert(`Failed to extract text from PDF: ${error.message}`);
                
                if (type === 'resume') {
                    setResumeFile(null);
                    setExtractionStatus(prev => ({ ...prev, resume: '❌ Extraction failed' }));
                } else {
                    setJobFile(null);
                    setExtractionStatus(prev => ({ ...prev, job: '❌ Extraction failed' }));
                }
                e.target.value = '';
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

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <div className="header-content">
                    <h1>AI-Free Skill Matcher</h1>
                    <p>Advanced rule-based skill matching and analysis</p>
                </div>
                <button className="logout-button" onClick={handleLogout}>
                    Logout
                </button>
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

                    <div className="match-button-container">
                        <button 
                            className="match-button" 
                            onClick={handleMatch} 
                            disabled={isLoading || (!resumeText.trim() && !resumeFile) || (!jdText.trim() && !jobFile)}
                        >
                            {isLoading ? (
                                <>
                                    <span className="spinner"></span>
                                    Analyzing Skills...
                                </>
                            ) : (
                                'Analyze & Match Skills'
                            )}
                        </button>
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
                                    <h3>Missing Skills (Learning Opportunities)</h3>
                                    <div className="skills-list missing-skills">
                                        {results.skills_analysis.missing_skills.map((skill, index) => (
                                            <span key={index} className="skill-tag missing">{skill}</span>
                                        ))}
                                        {results.skills_analysis.missing_skills.length === 0 && (
                                            <p className="no-skills">No missing skills - perfect match!</p>
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

                            {results.learning_path_recommendations && (
                                <div className="recommendations-section">
                                    <h3>Learning Path Recommendations</h3>
                                    
                                    {results.learning_path_recommendations.immediate_focus && 
                                     results.learning_path_recommendations.immediate_focus.length > 0 && (
                                        <div className="recommendation-group">
                                            <h4>🎯 Immediate Focus (Priority 1)</h4>
                                            <div className="recommendation-skills">
                                                {results.learning_path_recommendations.immediate_focus.map((skill, index) => (
                                                    <span key={index} className="skill-tag priority-high">{skill}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {results.learning_path_recommendations.short_term && 
                                     results.learning_path_recommendations.short_term.length > 0 && (
                                        <div className="recommendation-group">
                                            <h4>📈 Short-term Goals (Priority 2)</h4>
                                            <div className="recommendation-skills">
                                                {results.learning_path_recommendations.short_term.map((skill, index) => (
                                                    <span key={index} className="skill-tag priority-medium">{skill}</span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {results.learning_path_recommendations.learning_resources && 
                                     Object.keys(results.learning_path_recommendations.learning_resources).length > 0 && (
                                        <div className="learning-resources">
                                            <h4>📚 Learning Resources</h4>
                                            {Object.entries(results.learning_path_recommendations.learning_resources)
                                                .slice(0, 5)
                                                .map(([skill, resources]) => (
                                                <div key={skill} className="resource-group">
                                                    <h5>{skill}</h5>
                                                    <ul>
                                                        {resources.slice(0, 3).map((resource, index) => (
                                                            <li key={index}>{resource}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
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
        </div>
    );
};

export default SkillMatcherDashboard;