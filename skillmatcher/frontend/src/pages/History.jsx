import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './History.css';

const History = () => {
  const [selectedResume, setSelectedResume] = useState(null);
  const [history, setHistory] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Get user from localStorage
    const user = JSON.parse(localStorage.getItem('skillmatcher_user'));
    if (!user) return;
    fetch(`http://localhost:5000/history?email=${encodeURIComponent(user.email)}`)
      .then(res => res.json())
      .then(data => setHistory(data.history || []))
      .catch(() => setHistory([]));
  }, []);

  if (!history.length) {
    return (
      <div className="history-container">
        <h2>Analysis History</h2>
        <p style={{textAlign: 'center', color: '#aaa', margin: '2rem 0'}}>No history found. Start your first analysis!</p>
        <div style={{display: 'flex', justifyContent: 'center'}}>
          <button className="dashboard-btn" onClick={() => navigate('/analyze')}>Go to Analysis</button>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <h2>Analysis History</h2>
      <div className="resume-list">
        {history.map((resume, idx) => (
          <div
            key={resume.id || idx}
            className={`resume-item${selectedResume && selectedResume.id === resume.id ? ' selected' : ''}`}
            onClick={() => setSelectedResume(resume)}
          >
            <span className="resume-name">{resume.name}</span>
            <span className="resume-date">{resume.date}</span>
          </div>
        ))}
      </div>
      {selectedResume && (
        <div className="resume-result">
          <h3>Result for {selectedResume.name}</h3>
          <p>Status: <b>{selectedResume.result}</b></p>
          {/* Add more detailed results here as needed */}
        </div>
      )}
    </div>
  );
};

export default History;
