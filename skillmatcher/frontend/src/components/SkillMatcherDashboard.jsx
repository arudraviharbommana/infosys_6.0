
import React, { useState, useRef } from 'react';
import { API_BASE_URL } from '../config';


const SkillMatcherDashboard = ({ user, onLogout }) => {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [resumeText, setResumeText] = useState('');
  const [showResumePreview, setShowResumePreview] = useState(false);
  const [manualResumeText, setManualResumeText] = useState('');
  const [useManualInput, setUseManualInput] = useState(false);
  const [debugMode, setDebugMode] = useState(false);
  const [pdfStatus, setPdfStatus] = useState('ready');
  const fileInputRef = useRef(null);

  // Get the final resume text based on input mode
  const getFinalResumeText = () => {
    return useManualInput ? manualResumeText : resumeText;
  };

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    if (file.type !== 'application/pdf') {
      alert('Please upload a PDF file');
      setPdfStatus('❌ Please select a PDF file');
      return;
    }
    
    setResumeFile(file);
    setPdfStatus('🔄 Processing PDF...');
    
    try {
      if (debugMode) {
        console.log('Starting PDF processing for:', file.name);
        console.log('File size:', file.size, 'bytes');
        console.log('File type:', file.type);
      }
      
      // Use dynamic import with fallback
      let pdfjsLib;
      try {
        // Try the main build first
        pdfjsLib = await import('pdfjs-dist');
        // Set worker source
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjsLib.version}/build/pdf.worker.min.js`;
      } catch (importError) {
        if (debugMode) console.log('Main import failed, trying alternative...', importError);
        // Fallback to CDN
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
        document.head.appendChild(script);
        
        await new Promise((resolve, reject) => {
          script.onload = () => {
            if (window.pdfjsLib) {
              pdfjsLib = window.pdfjsLib;
              pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
              resolve();
            } else {
              reject(new Error('PDF.js not loaded'));
            }
          };
          script.onerror = reject;
        });
      }
      
      if (debugMode) {
        console.log('PDF.js loaded successfully');
        console.log('Version:', pdfjsLib.version);
        console.log('Worker source:', pdfjsLib.GlobalWorkerOptions.workerSrc);
      }
      
      // Read file as array buffer
      const arrayBuffer = await file.arrayBuffer();
      const typedArray = new Uint8Array(arrayBuffer);
      
      if (debugMode) {
        console.log('File read as ArrayBuffer, size:', typedArray.length);
      }
      
      setPdfStatus('📖 Loading PDF document...');
      
      // Load PDF document
      const loadingTask = pdfjsLib.getDocument({
        data: typedArray,
        cMapUrl: 'https://unpkg.com/pdfjs-dist@3.11.174/cmaps/',
        cMapPacked: true,
        disableFontFace: true, // Helps with compatibility
        verbosity: 0 // Reduce console output
      });
      
      const pdf = await loadingTask.promise;
      
      if (debugMode) {
        console.log('PDF loaded successfully. Pages:', pdf.numPages);
      }
      
      setPdfStatus(`📝 Extracting text from ${pdf.numPages} pages...`);
      
      let fullText = '';
      
      // Extract text from each page
      for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        try {
          const page = await pdf.getPage(pageNum);
          const textContent = await page.getTextContent();
          
          // Convert text items to string with proper spacing
          const pageText = textContent.items
            .map(item => {
              if (item.str && item.str.trim()) {
                return item.str.trim();
              }
              return '';
            })
            .filter(text => text.length > 0)
            .join(' ');
          
          fullText += pageText + '\n';
          
          if (debugMode) {
            console.log(`Page ${pageNum} processed: ${pageText.length} characters`);
          }
          
          setPdfStatus(`📝 Processing page ${pageNum}/${pdf.numPages}...`);
        } catch (pageError) {
          console.warn(`Error processing page ${pageNum}:`, pageError);
          if (debugMode) {
            console.error('Page processing error:', pageError);
          }
        }
      }
      
      // Clean up the extracted text
      fullText = fullText
        .replace(/\s+/g, ' ')  // Replace multiple spaces with single space
        .replace(/\n+/g, '\n') // Replace multiple newlines with single newline
        .trim();
      
      if (debugMode) {
        console.log('Text extraction complete');
        console.log('Total characters extracted:', fullText.length);
        console.log('Sample text (first 200 chars):', fullText.substring(0, 200));
      }
      
      setResumeText(fullText);
      
      if (fullText.length > 50) {
        setPdfStatus(`✅ Successfully extracted ${fullText.length} characters from ${pdf.numPages} pages`);
      } else {
        setPdfStatus('⚠️ PDF processed but minimal text found');
        alert('Very little text was extracted from the PDF. This might be a scanned document or image-based PDF. Please try the manual text input option.');
      }
      
    } catch (error) {
      console.error('PDF processing error:', error);
      setPdfStatus(`❌ Error: ${error.message}`);
      
      if (debugMode) {
        console.error('Full error details:', error);
      }
      
      // Provide helpful error message
      let errorMessage = 'Error processing PDF: ';
      if (error.message.includes('InvalidPDFException')) {
        errorMessage += 'The file appears to be corrupted or not a valid PDF.';
      } else if (error.message.includes('PasswordException')) {
        errorMessage += 'This PDF is password protected.';
      } else if (error.message.includes('Network')) {
        errorMessage += 'Network error. Please check your connection.';
      } else {
        errorMessage += error.message;
      }
      
      errorMessage += '\n\nPlease try:\n1. Using a different PDF file\n2. Using the manual text input option\n3. Refreshing the page and trying again';
      
      alert(errorMessage);
    }
  };

  // Handle analysis
  const handleAnalysis = async () => {
    const finalResumeText = getFinalResumeText();
    if (!finalResumeText.trim() || !jobDescription.trim()) {
      alert('Please provide both resume content and job description');
      return;
    }
    setIsAnalyzing(true);
    try {
      const user = JSON.parse(localStorage.getItem('skillmatcher_user'));
  const res = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resume_text: finalResumeText,
          jd_text: jobDescription,
          email: user.email
        })
      });
      if (!res.ok) throw new Error('Analysis failed');
      const results = await res.json();
      setAnalysisResults(results);
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Error during analysis: ' + error.message + '. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Reset analysis
  const handleReset = () => {
    setResumeFile(null);
    setJobDescription('');
    setAnalysisResults(null);
    setResumeText('');
    setManualResumeText('');
    setShowResumePreview(false);
    setPdfStatus('ready');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1 className="dashboard-title">SkillMatcher Dashboard</h1>
          <div className="user-info">
            <span>Welcome, {user.username || user.email}</span>
            <label className="debug-toggle">
              <input
                type="checkbox"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
              />
              Debug Mode
            </label>
            <button onClick={onLogout} className="logout-btn">Logout</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-main">
        {/* Input Section */}
        <div className="input-section">
          {/* Debug Toggle */}
          <div className="debug-toggle">
            <label>
              <input
                type="checkbox"
                checked={debugMode}
                onChange={(e) => setDebugMode(e.target.checked)}
              />
              Debug Mode (Console Logging)
            </label>
          </div>

          {/* Input Mode Toggle */}
          <div className="input-mode-toggle">
            <button
              className={`mode-btn ${!useManualInput ? 'active' : ''}`}
              onClick={() => setUseManualInput(false)}
            >
              📄 PDF Upload
            </button>
            <button
              className={`mode-btn ${useManualInput ? 'active' : ''}`}
              onClick={() => setUseManualInput(true)}
            >
              ✏️ Manual Input
            </button>
          </div>

          {/* PDF Upload Section */}
          {!useManualInput && (
            <div className="upload-area">
              <h3>Upload Resume (PDF)</h3>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="file-input"
              />
              {resumeFile && (
                <div className="file-info">
                  ✓ {resumeFile.name}
                  <div className="pdf-status">
                    <span className={`status-indicator ${pdfStatus.includes('✅') ? 'success' : pdfStatus.includes('❌') ? 'error' : pdfStatus.includes('⚠️') ? 'warning' : 'processing'}`}>
                      {pdfStatus || 'Ready'}
                    </span>
                  </div>
                  {resumeText && (
                    <button
                      className="preview-btn"
                      onClick={() => setShowResumePreview(!showResumePreview)}
                    >
                      {showResumePreview ? 'Hide' : 'Show'} Extracted Text
                    </button>
                  )}
                </div>
              )}
              
              {/* Resume Preview */}
              {showResumePreview && resumeText && (
                <div className="resume-preview">
                  <h4>Extracted Resume Text:</h4>
                  <div className="preview-text">
                    {resumeText.substring(0, 1000)}
                    {resumeText.length > 1000 && '...'}
                  </div>
                  <p className="preview-info">
                    Total characters: {resumeText.length} | 
                    Showing first 1000 characters
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Manual Input Section */}
          {useManualInput && (
            <div className="manual-input-area">
              <h3>Paste Resume Text</h3>
              <textarea
                value={manualResumeText}
                onChange={(e) => setManualResumeText(e.target.value)}
                placeholder="Paste your complete resume text here..."
                className="manual-resume-textarea"
                rows="12"
              />
              <p className="input-info">
                Characters: {manualResumeText.length}
              </p>
            </div>
          )}

          <div className="job-description-area">
            <h3>Job Description</h3>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job description here..."
              className="job-textarea"
              rows="8"
            />
            <p className="input-info">
              Characters: {jobDescription.length}
            </p>
          </div>

          <div className="action-buttons">
            <button
              onClick={handleAnalysis}
              disabled={isAnalyzing || !getFinalResumeText().trim() || !jobDescription.trim()}
              className="analyze-btn"
            >
              {isAnalyzing ? 'Analyzing Skills...' : 'Analyze Skills Match'}
            </button>
            <button onClick={handleReset} className="reset-btn">
              Reset All
            </button>
          </div>
        </div>

        {/* Results Section */}
        {analysisResults && (
          <div className="results-section">
            {/* Overall Score */}
            <div className="score-card">
              <h2>Overall Match Score</h2>
              <div className="score-display">
                <div className="score-circle">
                  <span className="score-number">{analysisResults.overallScore}%</span>
                </div>
                <div className="score-details">
                  <p>Total Skills Found: {analysisResults.totalSkills}</p>
                  <p>Matched Skills: {analysisResults.matchedSkills}</p>
                  <p>Strong Matches: {analysisResults.analysis.strongMatches}</p>
                  <p>Partial Matches: {analysisResults.analysis.partialMatches}</p>
                </div>
              </div>
            </div>

            {/* Skills Analysis Tables */}
            <div className="skills-analysis-section">
              {/* Resume Skills Table */}
              <div className="skills-table-container">
                <h3>📄 Resume Skills Analysis</h3>
                <div className="table-wrapper">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>Skill</th>
                        <th>Category</th>
                        <th>Confidence</th>
                        <th>Match Status</th>
                        <th>Context</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisResults.resumeSkills.map((skill, index) => {
                        const isExactMatch = analysisResults.exactMatches.some(match => match.name === skill.name);
                        
                        // Check different levels of semantic matches
                        const strongMatch = analysisResults.semanticMatches.strong?.find(match => match.resumeSkill === skill.name);
                        const moderateMatch = analysisResults.semanticMatches.moderate?.find(match => match.resumeSkill === skill.name);
                        const weakMatch = analysisResults.semanticMatches.weak?.find(match => match.resumeSkill === skill.name);
                        
                        // Fallback for legacy format
                        const legacyMatch = (!strongMatch && !moderateMatch && !weakMatch && analysisResults.semanticMatches.all) ? 
                          analysisResults.semanticMatches.all.find(match => match.resumeSkill === skill.name) : null;
                        
                        const semanticMatch = strongMatch || moderateMatch || weakMatch || legacyMatch;
                        const matchStatus = isExactMatch ? 'exact' : 
                                          strongMatch ? 'strong' :
                                          moderateMatch ? 'moderate' :
                                          weakMatch ? 'weak' :
                                          legacyMatch ? 'partial' : 'no-match';
                        
                        return (
                          <tr key={index} className={`skill-row ${matchStatus}`}>
                            <td className="skill-name" data-label="Skill">{skill.name}</td>
                            <td className="skill-category" data-label="Category">{skill.category}</td>
                            <td className="confidence" data-label="Confidence">
                              <div className="confidence-bar">
                                <div 
                                  className="confidence-fill" 
                                  style={{width: `${skill.confidence * 100}%`}}
                                ></div>
                                <span className="confidence-text">{Math.round(skill.confidence * 100)}%</span>
                              </div>
                            </td>
                            <td className="match-status" data-label="Match Status">
                              {isExactMatch && <span className="status-badge exact">✓ Exact Match</span>}
                              {strongMatch && <span className="status-badge strong">✓ Strong Match ({Math.round(strongMatch.similarity * 100)}%)</span>}
                              {moderateMatch && <span className="status-badge moderate">≈ Moderate Match ({Math.round(moderateMatch.similarity * 100)}%)</span>}
                              {weakMatch && <span className="status-badge weak">~ Weak Match ({Math.round(weakMatch.similarity * 100)}%)</span>}
                              {legacyMatch && <span className="status-badge partial">≈ {Math.round(legacyMatch.similarity * 100)}% Similar</span>}
                              {!isExactMatch && !semanticMatch && <span className="status-badge no-match">No Match</span>}
                            </td>
                            <td className="context" data-label="Context" title={skill.context}>
                              {skill.context ? skill.context.substring(0, 50) + '...' : 'N/A'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Job Description Skills Table */}
              <div className="skills-table-container">
                <h3>💼 Job Description Skills Analysis</h3>
                <div className="table-wrapper">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>Skill</th>
                        <th>Category</th>
                        <th>Priority</th>
                        <th>Match Status</th>
                        <th>Context</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisResults.jobSkills.map((skill, index) => {
                        const isExactMatch = analysisResults.exactMatches.some(match => match.name === skill.name);
                        
                        // Check different levels of semantic matches
                        const strongMatch = analysisResults.semanticMatches.strong?.find(match => match.jobSkill === skill.name);
                        const moderateMatch = analysisResults.semanticMatches.moderate?.find(match => match.jobSkill === skill.name);
                        const weakMatch = analysisResults.semanticMatches.weak?.find(match => match.jobSkill === skill.name);
                        
                        // Fallback for legacy format
                        const legacyMatch = (!strongMatch && !moderateMatch && !weakMatch && analysisResults.semanticMatches.all) ? 
                          analysisResults.semanticMatches.all.find(match => match.jobSkill === skill.name) : null;
                        
                        const semanticMatch = strongMatch || moderateMatch || weakMatch || legacyMatch;
                        const matchStatus = isExactMatch ? 'exact' : 
                                          strongMatch ? 'strong' :
                                          moderateMatch ? 'moderate' :
                                          weakMatch ? 'weak' :
                                          legacyMatch ? 'partial' : 'missing';
                        
                        return (
                          <tr key={index} className={`skill-row ${matchStatus}`}>
                            <td className="skill-name" data-label="Skill">{skill.name}</td>
                            <td className="skill-category" data-label="Category">{skill.category}</td>
                            <td className="priority" data-label="Priority">
                              <span className={`priority-badge ${skill.priority}`}>
                                {skill.priority}
                              </span>
                            </td>
                            <td className="match-status" data-label="Match Status">
                              {isExactMatch && <span className="status-badge exact">✓ Found in Resume</span>}
                              {strongMatch && <span className="status-badge strong">✓ Strong Match: {strongMatch.resumeSkill}</span>}
                              {moderateMatch && <span className="status-badge moderate">≈ Moderate: {moderateMatch.resumeSkill}</span>}
                              {weakMatch && <span className="status-badge weak">~ Weak: {weakMatch.resumeSkill}</span>}
                              {legacyMatch && <span className="status-badge partial">≈ Similar: {legacyMatch.resumeSkill}</span>}
                              {!isExactMatch && !semanticMatch && <span className="status-badge missing">⚠ Missing</span>}
                            </td>
                            <td className="context" data-label="Context" title={skill.context}>
                              {skill.context ? skill.context.substring(0, 50) + '...' : 'N/A'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Skills Matching Summary Table */}
              <div className="skills-table-container">
                <h3>🔄 Skills Matching Summary</h3>
                <div className="table-wrapper">
                  <table className="skills-table">
                    <thead>
                      <tr>
                        <th>Resume Skill</th>
                        <th>Job Skill</th>
                        <th>Match Type</th>
                        <th>Similarity Score</th>
                        <th>Category</th>
                        <th>Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      {/* Exact Matches */}
                      {analysisResults.exactMatches.map((match, index) => {
                        const jobSkill = analysisResults.jobSkills.find(js => js.name === match.name);
                        return (
                          <tr key={`exact-${index}`} className="skill-row exact">
                            <td className="skill-name" data-label="Resume Skill">{match.name}</td>
                            <td className="skill-name" data-label="Job Skill">{match.name}</td>
                            <td className="match-type" data-label="Match Type">
                              <span className="match-badge exact">Exact Match</span>
                            </td>
                            <td className="similarity-score" data-label="Similarity Score">
                              <div className="score-bar">
                                <div className="score-fill exact" style={{width: '100%'}}></div>
                                <span className="score-text">100%</span>
                              </div>
                            </td>
                            <td className="skill-category" data-label="Category">{match.category}</td>
                            <td className="priority" data-label="Priority">
                              <span className={`priority-badge ${jobSkill?.priority || 'mentioned'}`}>
                                {jobSkill?.priority || 'mentioned'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      
                      {/* Semantic Matches */}
                      {/* Strong Matches (60%+) */}
                      {analysisResults.semanticMatches.strong?.map((match, index) => {
                        const jobSkill = analysisResults.jobSkills.find(js => js.name === match.jobSkill);
                        return (
                          <tr key={`strong-${index}`} className="skill-row strong">
                            <td className="skill-name" data-label="Resume Skill">{match.resumeSkill}</td>
                            <td className="skill-name" data-label="Job Skill">{match.jobSkill}</td>
                            <td className="match-type" data-label="Match Type">
                              <span className="match-badge strong">Strong Match</span>
                            </td>
                            <td className="similarity-score" data-label="Similarity Score">
                              <div className="score-bar">
                                <div 
                                  className="score-fill strong" 
                                  style={{width: `${match.similarity * 100}%`}}
                                ></div>
                                <span className="score-text">{Math.round(match.similarity * 100)}%</span>
                              </div>
                            </td>
                            <td className="skill-category" data-label="Category">{match.category}</td>
                            <td className="priority" data-label="Priority">
                              <span className={`priority-badge ${jobSkill?.priority || 'mentioned'}`}>
                                {jobSkill?.priority || 'mentioned'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      
                      {/* Moderate Matches (50-59%) */}
                      {analysisResults.semanticMatches.moderate?.map((match, index) => {
                        const jobSkill = analysisResults.jobSkills.find(js => js.name === match.jobSkill);
                        return (
                          <tr key={`moderate-${index}`} className="skill-row moderate">
                            <td className="skill-name" data-label="Resume Skill">{match.resumeSkill}</td>
                            <td className="skill-name" data-label="Job Skill">{match.jobSkill}</td>
                            <td className="match-type" data-label="Match Type">
                              <span className="match-badge moderate">Moderate Match</span>
                            </td>
                            <td className="similarity-score" data-label="Similarity Score">
                              <div className="score-bar">
                                <div 
                                  className="score-fill moderate" 
                                  style={{width: `${match.similarity * 100}%`}}
                                ></div>
                                <span className="score-text">{Math.round(match.similarity * 100)}%</span>
                              </div>
                            </td>
                            <td className="skill-category" data-label="Category">{match.category}</td>
                            <td className="priority" data-label="Priority">
                              <span className={`priority-badge ${jobSkill?.priority || 'mentioned'}`}>
                                {jobSkill?.priority || 'mentioned'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      
                      {/* Weak Matches (30-49%) - Show only first 5 */}
                      {analysisResults.semanticMatches.weak?.slice(0, 5).map((match, index) => {
                        const jobSkill = analysisResults.jobSkills.find(js => js.name === match.jobSkill);
                        return (
                          <tr key={`weak-${index}`} className="skill-row weak">
                            <td className="skill-name" data-label="Resume Skill">{match.resumeSkill}</td>
                            <td className="skill-name" data-label="Job Skill">{match.jobSkill}</td>
                            <td className="match-type" data-label="Match Type">
                              <span className="match-badge weak">Weak Match</span>
                            </td>
                            <td className="similarity-score" data-label="Similarity Score">
                              <div className="score-bar">
                                <div 
                                  className="score-fill weak" 
                                  style={{width: `${match.similarity * 100}%`}}
                                ></div>
                                <span className="score-text">{Math.round(match.similarity * 100)}%</span>
                              </div>
                            </td>
                            <td className="skill-category" data-label="Category">{match.category}</td>
                            <td className="priority" data-label="Priority">
                              <span className={`priority-badge ${jobSkill?.priority || 'mentioned'}`}>
                                {jobSkill?.priority || 'mentioned'}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      
                      {/* Fallback for legacy format */}
                      {(!analysisResults.semanticMatches.strong && !analysisResults.semanticMatches.moderate && !analysisResults.semanticMatches.weak && analysisResults.semanticMatches.slice) ? 
                        analysisResults.semanticMatches.slice(0, 10).map((match, index) => {
                          const jobSkill = analysisResults.jobSkills.find(js => js.name === match.jobSkill);
                          return (
                            <tr key={`semantic-${index}`} className="skill-row partial">
                              <td className="skill-name" data-label="Resume Skill">{match.resumeSkill}</td>
                              <td className="skill-name" data-label="Job Skill">{match.jobSkill}</td>
                              <td className="match-type" data-label="Match Type">
                                <span className="match-badge partial">Semantic Match</span>
                              </td>
                              <td className="similarity-score" data-label="Similarity Score">
                                <div className="score-bar">
                                  <div 
                                    className="score-fill partial" 
                                    style={{width: `${match.similarity * 100}%`}}
                                  ></div>
                                  <span className="score-text">{Math.round(match.similarity * 100)}%</span>
                                </div>
                              </td>
                              <td className="skill-category" data-label="Category">{match.category}</td>
                              <td className="priority" data-label="Priority">
                                <span className={`priority-badge ${jobSkill?.priority || 'mentioned'}`}>
                                  {jobSkill?.priority || 'mentioned'}
                                </span>
                              </td>
                            </tr>
                          );
                        }) : null
                      }
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Enhanced Suggestions */}
            {analysisResults.suggestions.length > 0 && (
              <div className="suggestions-section">
                <h3>🎯 AI-Powered Skill Recommendations</h3>
                <div className="suggestions-list">
                  {analysisResults.suggestions.map((suggestion, index) => (
                    <div key={index} className={`suggestion-card ${suggestion.priority} ${suggestion.urgency}`}>
                      <div className="suggestion-header">
                        <span className="suggestion-type">
                          {suggestion.type === 'critical_skill_gap' ? '🚨' : 
                           suggestion.type === 'skill_improvement_needed' ? '⚠️' :
                           suggestion.type === 'skill_enhancement' ? '💡' : '✨'}
                        </span>
                        <span className="suggestion-skill">{suggestion.skill}</span>
                        <div className="suggestion-badges">
                          <span className={`priority-badge ${suggestion.priority}`}>
                            {suggestion.priority}
                          </span>
                          {suggestion.urgency && (
                            <span className={`urgency-badge ${suggestion.urgency}`}>
                              {suggestion.urgency} urgency
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <p className="suggestion-text">{suggestion.suggestion}</p>
                      
                      {suggestion.currentSkill && (
                        <div className="current-skill-info">
                          <strong>Your current skill:</strong> {suggestion.currentSkill} 
                          <span className="similarity-info">({Math.round(suggestion.similarity * 100)}% match)</span>
                        </div>
                      )}
                      
                      <div className="suggestion-details">
                        <div className="detail-item">
                          <span className="detail-label">⏱️ Learning Time:</span>
                          <span className="detail-value">{suggestion.estimatedLearningTime}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">📊 Difficulty:</span>
                          <span className={`difficulty-badge ${suggestion.difficultyLevel?.toLowerCase()}`}>
                            {suggestion.difficultyLevel}
                          </span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">🎯 Category:</span>
                          <span className="category-badge">{suggestion.category}</span>
                        </div>
                      </div>
                      
                      <div className="resources">
                        <strong>📚 Learning Resources:</strong>
                        <div className="resource-list">
                          {suggestion.resources.map((resource, idx) => (
                            <span key={idx} className="resource-tag">{resource}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      <style jsx>{`
        .dashboard {
          min-height: 100vh;
          background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
          color: white;
          overflow-x: hidden;
        }

        .dashboard-header {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(255, 255, 255, 0.2);
          padding: 1rem 2rem;
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .header-content {
          display: flex;
          justify-content: space-between;
          align-items: center;
          max-width: 1200px;
          margin: 0 auto;
          width: 100%;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .dashboard-title {
          font-size: 1.8rem;
          font-weight: 600;
          background: linear-gradient(135deg, #00aaff, #ff00aa);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          white-space: nowrap;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .logout-btn {
          padding: 0.5rem 1rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .logout-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .dashboard-main {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          width: 100%;
          box-sizing: border-box;
        }

        .input-section {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 20px;
          padding: 2rem;
          margin-bottom: 2rem;
        }

        .debug-toggle {
          margin-bottom: 1rem;
          padding: 0.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 8px;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .debug-toggle label {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9rem;
          cursor: pointer;
        }

        .input-mode-toggle {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 12px;
          padding: 0.3rem;
        }

        .mode-btn {
          flex: 1;
          padding: 0.8rem 1rem;
          border: none;
          border-radius: 8px;
          background: transparent;
          color: rgba(255, 255, 255, 0.7);
          font-size: 0.9rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .mode-btn.active {
          background: linear-gradient(135deg, #00aaff, #ff00aa);
          color: white;
          box-shadow: 0 2px 10px rgba(0, 170, 255, 0.3);
        }

        .mode-btn:hover:not(.active) {
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }

        .upload-area, .manual-input-area, .job-description-area {
          margin-bottom: 1.5rem;
        }

        .manual-input-area {
          display: block;
        }

        .manual-resume-textarea {
          width: 100%;
          padding: 1rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          resize: vertical;
          font-family: inherit;
          line-height: 1.5;
        }

        .manual-resume-textarea::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        .manual-resume-textarea:focus {
          outline: none;
          border-color: #00aaff;
          box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
        }

        .preview-btn {
          padding: 0.5rem 1rem;
          margin-top: 0.5rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          cursor: pointer;
          font-size: 0.9rem;
          transition: all 0.3s ease;
        }

        .preview-btn:hover {
          background: rgba(255, 255, 255, 0.2);
          border-color: #00aaff;
        }

        .resume-preview {
          margin-top: 1rem;
          padding: 1rem;
          background: rgba(0, 0, 0, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
        }

        .resume-preview h4 {
          color: #00aaff;
          margin-bottom: 0.5rem;
          font-size: 1rem;
        }

        .preview-text {
          background: rgba(255, 255, 255, 0.05);
          padding: 1rem;
          border-radius: 8px;
          font-family: 'Courier New', monospace;
          font-size: 0.8rem;
          line-height: 1.4;
          white-space: pre-wrap;
          word-wrap: break-word;
          max-height: 200px;
          overflow-y: auto;
          color: rgba(255, 255, 255, 0.9);
        }

        .preview-info, .input-info {
          font-size: 0.8rem;
          color: rgba(255, 255, 255, 0.6);
          margin-top: 0.5rem;
        }

        .upload-area h3, .manual-input-area h3, .job-description-area h3 {
          margin-bottom: 0.5rem;
          color: #00aaff;
        }

        .file-input {
          width: 100%;
          padding: 0.8rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }

        .file-info {
          margin-top: 0.5rem;
          color: #00ff88;
          font-size: 0.9rem;
        }

        .pdf-status {
          margin-top: 0.3rem;
          font-size: 0.8rem;
        }

        .status-indicator {
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          font-weight: 500;
        }

        .status-indicator.success {
          background: rgba(0, 255, 136, 0.2);
          color: #00ff88;
          border: 1px solid #00ff88;
        }

        .status-indicator.error {
          background: rgba(255, 68, 68, 0.2);
          color: #ff4444;
          border: 1px solid #ff4444;
        }

        .status-indicator.warning {
          background: rgba(255, 170, 0, 0.2);
          color: #ffaa00;
          border: 1px solid #ffaa00;
        }

        .status-indicator.processing {
          background: rgba(0, 170, 255, 0.2);
          color: #00aaff;
          border: 1px solid #00aaff;
        }

        .debug-toggle {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.9rem;
          color: rgba(255, 255, 255, 0.8);
          cursor: pointer;
        }

        .debug-toggle input[type="checkbox"] {
          margin: 0;
        }

        .text-input-alternative {
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid rgba(255, 255, 255, 0.2);
        }

        .text-input-alternative p {
          margin-bottom: 0.5rem;
          color: rgba(255, 255, 255, 0.8);
          font-size: 0.9rem;
        }

        .resume-textarea {
          width: 100%;
          padding: 1rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          resize: vertical;
          font-family: inherit;
          font-size: 0.9rem;
        }

        .resume-textarea::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        .job-textarea {
          width: 100%;
          padding: 1rem;
          border: 1px solid rgba(255, 255, 255, 0.3);
          border-radius: 8px;
          background: rgba(255, 255, 255, 0.1);
          color: white;
          resize: vertical;
          font-family: inherit;
        }

        .job-textarea::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .analyze-btn, .reset-btn {
          padding: 1rem 2rem;
          border: none;
          border-radius: 12px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          flex: 1;
          min-width: 120px;
        }

        .analyze-btn {
          background: linear-gradient(135deg, #00aaff, #ff00aa);
          color: white;
        }

        .analyze-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .analyze-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(0, 170, 255, 0.4);
        }

        .reset-btn {
          background: rgba(255, 255, 255, 0.1);
          color: white;
          border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .reset-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .results-section {
          display: grid;
          gap: 2rem;
        }

        .score-card {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 20px;
          padding: 2rem;
          text-align: center;
        }

        .score-display {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 2rem;
          margin-top: 1rem;
          flex-wrap: wrap;
        }

        .score-circle {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          background: conic-gradient(from 0deg, #00aaff, #ff00aa, #00aaff);
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
        }

        .score-circle::before {
          content: '';
          position: absolute;
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: rgba(0, 0, 0, 0.8);
        }

        .score-number {
          position: relative;
          font-size: 1.5rem;
          font-weight: bold;
          color: white;
        }

        .score-details {
          text-align: left;
        }

        .score-details p {
          margin: 0.5rem 0;
          color: rgba(255, 255, 255, 0.8);
        }

        .matches-section, .suggestions-section, .skills-analysis-section {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 20px;
          padding: 2rem;
        }

        .skills-analysis-section {
          display: grid;
          gap: 2rem;
        }

        .skills-table-container {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 15px;
          padding: 1.5rem;
          border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .skills-table-container h3 {
          margin-bottom: 1rem;
          color: #00aaff;
          font-size: 1.2rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .table-wrapper {
          overflow-x: auto;
          border-radius: 10px;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .skills-table {
          width: 100%;
          border-collapse: collapse;
          background: rgba(0, 0, 0, 0.3);
          font-size: 0.9rem;
        }

        .skills-table th {
          background: rgba(0, 170, 255, 0.2);
          color: white;
          padding: 1rem 0.8rem;
          text-align: left;
          font-weight: 600;
          border-bottom: 2px solid rgba(0, 170, 255, 0.5);
          position: sticky;
          top: 0;
          z-index: 10;
        }

        .skills-table td {
          padding: 0.8rem;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
          vertical-align: middle;
        }

        .skill-row {
          transition: all 0.3s ease;
        }

        .skill-row:hover {
          background: rgba(255, 255, 255, 0.05);
        }

        .skill-row.exact {
          background: rgba(0, 255, 136, 0.05);
          border-left: 3px solid #00ff88;
        }

        .skill-row.strong {
          background: rgba(0, 170, 255, 0.05);
          border-left: 3px solid #00aaff;
        }

        .skill-row.moderate {
          background: rgba(255, 170, 0, 0.05);
          border-left: 3px solid #ffaa00;
        }

        .skill-row.weak {
          background: rgba(255, 136, 0, 0.05);
          border-left: 3px solid #ff8800;
        }

        .skill-row.partial {
          background: rgba(255, 170, 0, 0.05);
          border-left: 3px solid #ffaa00;
        }

        .skill-row.no-match,
        .skill-row.missing {
          background: rgba(255, 68, 68, 0.05);
          border-left: 3px solid #ff4444;
        }

        .skill-name {
          font-weight: 600;
          color: #00aaff;
          min-width: 120px;
        }

        .skill-category {
          color: rgba(255, 255, 255, 0.7);
          font-size: 0.8rem;
          min-width: 100px;
        }

        .confidence-bar,
        .score-bar {
          position: relative;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 10px;
          height: 20px;
          min-width: 80px;
          overflow: hidden;
        }

        .confidence-fill,
        .score-fill {
          height: 100%;
          border-radius: 10px;
          transition: width 0.3s ease;
        }

        .confidence-fill {
          background: linear-gradient(90deg, #ff4444, #ffaa00, #00ff88);
        }

        .score-fill.exact {
          background: linear-gradient(90deg, #00ff88, #00aaff);
        }

        .score-fill.strong {
          background: linear-gradient(90deg, #00aaff, #0099dd);
        }

        .score-fill.moderate {
          background: linear-gradient(90deg, #ffaa00, #ff9900);
        }

        .score-fill.weak {
          background: linear-gradient(90deg, #ff8800, #ff7700);
        }

        .score-fill.partial {
          background: linear-gradient(90deg, #ffaa00, #ff6600);
        }

        .confidence-text,
        .score-text {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          font-size: 0.7rem;
          font-weight: 600;
          color: white;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }

        .status-badge,
        .match-badge {
          padding: 0.3rem 0.6rem;
          border-radius: 12px;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          white-space: nowrap;
        }

        .status-badge.exact,
        .match-badge.exact {
          background: #00ff88;
          color: #000;
        }

        .status-badge.strong,
        .match-badge.strong {
          background: #00aaff;
          color: #000;
        }

        .status-badge.moderate,
        .match-badge.moderate {
          background: #ffaa00;
          color: #000;
        }

        .status-badge.weak,
        .match-badge.weak {
          background: #ff8800;
          color: #000;
        }

        .status-badge.partial,
        .match-badge.partial {
          background: #ffaa00;
          color: #000;
        }

        .status-badge.no-match,
        .status-badge.missing {
          background: #ff4444;
          color: white;
        }

        .priority-badge {
          padding: 0.2rem 0.5rem;
          border-radius: 8px;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
          white-space: nowrap;
        }

        .priority-badge.required {
          background: #ff4444;
          color: white;
        }

        .priority-badge.preferred {
          background: #ffaa00;
          color: black;
        }

        .priority-badge.mentioned {
          background: rgba(255, 255, 255, 0.2);
          color: rgba(255, 255, 255, 0.8);
        }

        .context {
          color: rgba(255, 255, 255, 0.6);
          font-size: 0.8rem;
          max-width: 200px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          cursor: help;
        }

        .match-type {
          min-width: 100px;
        }

        .similarity-score {
          min-width: 100px;
        }

        .match-group {
          margin-bottom: 1.5rem;
        }

        .match-group h4 {
          color: #00aaff;
          margin-bottom: 1rem;
        }

        .skill-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 0.5rem;
        }

        .skill-tag {
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 8px;
          padding: 0.5rem;
          font-size: 0.9rem;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .skill-tag.exact {
          border-color: #00ff88;
          background: rgba(0, 255, 136, 0.1);
        }

        .skill-tag.semantic {
          border-color: #ffaa00;
          background: rgba(255, 170, 0, 0.1);
        }

        .skill-category, .similarity {
          font-size: 0.7rem;
          color: rgba(255, 255, 255, 0.6);
        }

        .suggestions-list {
          display: grid;
          gap: 1rem;
        }

        .suggestion-card {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 12px;
          padding: 1rem;
        }

        .suggestion-card.critical {
          border-color: #ff0000;
          background: rgba(255, 0, 0, 0.15);
          box-shadow: 0 0 20px rgba(255, 0, 0, 0.3);
        }

        .suggestion-card.high {
          border-color: #ff4444;
          background: rgba(255, 68, 68, 0.1);
        }

        .suggestion-card.medium {
          border-color: #ffaa00;
          background: rgba(255, 170, 0, 0.1);
        }

        .suggestion-card.low {
          border-color: #00aaff;
          background: rgba(0, 170, 255, 0.1);
        }

        .suggestion-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          flex-wrap: wrap;
        }

        .suggestion-badges {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .urgency-badge {
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          font-size: 0.6rem;
          font-weight: 600;
          text-transform: uppercase;
          white-space: nowrap;
        }

        .urgency-badge.high {
          background: #ff0000;
          color: white;
        }

        .urgency-badge.medium {
          background: #ff8800;
          color: white;
        }

        .urgency-badge.low {
          background: #00aaff;
          color: white;
        }

        .current-skill-info {
          background: rgba(255, 255, 255, 0.05);
          padding: 0.5rem;
          border-radius: 6px;
          margin: 0.5rem 0;
          font-size: 0.9rem;
        }

        .similarity-info {
          color: #00aaff;
          font-weight: 600;
          margin-left: 0.5rem;
        }

        .suggestion-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 0.5rem;
          margin: 0.75rem 0;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          font-size: 0.8rem;
        }

        .detail-label {
          font-weight: 500;
          color: rgba(255, 255, 255, 0.7);
        }

        .detail-value {
          color: white;
          font-weight: 600;
        }

        .difficulty-badge {
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: capitalize;
        }

        .difficulty-badge.beginner {
          background: #00ff88;
          color: #000;
        }

        .difficulty-badge.intermediate {
          background: #ffaa00;
          color: #000;
        }

        .difficulty-badge.advanced {
          background: #ff4444;
          color: white;
        }

        .category-badge {
          background: rgba(0, 170, 255, 0.2);
          color: #00aaff;
          padding: 0.1rem 0.4rem;
          border-radius: 4px;
          font-size: 0.7rem;
          font-weight: 600;
        }

        .resources {
          margin-top: 0.75rem;
        }

        .resource-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.25rem;
          margin-top: 0.5rem;
        }

        .suggestion-skill {
          font-weight: 600;
          color: #00aaff;
        }

        .priority-badge {
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          font-size: 0.7rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .priority-badge.high {
          background: #ff4444;
          color: white;
        }

        .priority-badge.medium {
          background: #ffaa00;
          color: black;
        }

        .resources {
          margin-top: 0.5rem;
          display: flex;
          flex-wrap: wrap;
          gap: 0.25rem;
          align-items: center;
        }

        .resource-tag {
          background: rgba(255, 255, 255, 0.1);
          padding: 0.2rem 0.5rem;
          border-radius: 4px;
          font-size: 0.7rem;
          margin-left: 0.5rem;
        }

        @media (max-width: 768px) {
          .dashboard-main {
            padding: 1rem;
          }
          
          .dashboard-header {
            padding: 1rem;
          }
          
          .header-content {
            flex-direction: column;
            text-align: center;
            gap: 0.5rem;
          }
          
          .dashboard-title {
            font-size: 1.5rem;
          }
          
          .score-display {
            flex-direction: column;
            gap: 1rem;
          }
          
          .action-buttons {
            flex-direction: column;
          }
          
          .analyze-btn, .reset-btn {
            width: 100%;
            flex: none;
          }
          
          .skill-grid {
            grid-template-columns: 1fr;
          }
          
          .user-info {
            justify-content: center;
          }
          
          .file-input,
          .job-textarea {
            font-size: 16px; /* Prevents zoom on iOS */
          }

          /* Table responsive styles */
          .skills-table-container {
            padding: 1rem;
          }

          .skills-table {
            font-size: 0.8rem;
          }

          .skills-table th,
          .skills-table td {
            padding: 0.5rem 0.4rem;
          }

          .table-wrapper {
            border-radius: 8px;
          }

          .confidence-bar,
          .score-bar {
            min-width: 60px;
            height: 16px;
          }

          .confidence-text,
          .score-text {
            font-size: 0.6rem;
          }

          .status-badge,
          .match-badge,
          .priority-badge {
            padding: 0.2rem 0.4rem;
            font-size: 0.6rem;
          }

          .context {
            max-width: 120px;
            font-size: 0.7rem;
          }

          .skill-name {
            min-width: 80px;
          }

          .skill-category {
            min-width: 80px;
          }
        }

        @media (max-width: 480px) {
          .dashboard-main {
            padding: 0.5rem;
          }
          
          .input-section,
          .score-card,
          .matches-section,
          .suggestions-section,
          .skills-analysis-section {
            padding: 1rem;
            margin-bottom: 1rem;
          }
          
          .dashboard-title {
            font-size: 1.2rem;
          }
          
          .score-circle {
            width: 100px;
            height: 100px;
          }
          
          .score-circle::before {
            width: 80px;
            height: 80px;
          }
          
          .score-number {
            font-size: 1.2rem;
          }

          /* Mobile table styles */
          .skills-analysis-section {
            gap: 1rem;
          }

          .skills-table-container {
            padding: 0.8rem;
          }

          .skills-table-container h3 {
            font-size: 1rem;
            margin-bottom: 0.8rem;
          }

          .skills-table {
            font-size: 0.7rem;
          }

          .skills-table th,
          .skills-table td {
            padding: 0.4rem 0.3rem;
          }

          .confidence-bar,
          .score-bar {
            min-width: 50px;
            height: 14px;
          }

          .context {
            max-width: 100px;
          }

          /* Stack table cells on very small screens */
          .skills-table thead {
            display: none;
          }

          .skills-table,
          .skills-table tbody,
          .skills-table tr,
          .skills-table td {
            display: block;
          }

          .skills-table tr {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
          }

          .skills-table td {
            border: none;
            padding: 0.3rem 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
          }

          .skills-table td:before {
            content: attr(data-label) ": ";
            font-weight: 600;
            color: #00aaff;
            flex: 0 0 auto;
            margin-right: 1rem;
          }
        }

        @media (max-width: 320px) {
          .dashboard-main {
            padding: 0.25rem;
          }
          
          .input-section,
          .score-card,
          .matches-section,
          .suggestions-section {
            padding: 0.75rem;
          }
          
          .analyze-btn, .reset-btn {
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
          }
          
          .dashboard-title {
            font-size: 1rem;
          }
        }

        /* Landscape tablets */
        @media (min-width: 769px) and (max-width: 1024px) {
          .dashboard-main {
            padding: 1.5rem;
          }
          
          .skill-grid {
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
          }
        }

        /* Large screens */
        @media (min-width: 1200px) {
          .dashboard-main {
            max-width: 1400px;
          }
          
          .skill-grid {
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          }
        }
      `}</style>
    </div>
  );
};

export default SkillMatcherDashboard;