import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import History from './components/History';
import SkillMatcherDashboard from './components/SkillMatcherDashboard';
import ResultDetailsPage from './components/ResultDetailsPage';
import Sidebar from './components/Sidebar';
import ThreeDScene from './components/ThreeDScene';
import './styles/main.css';

// Configure axios defaults
axios.defaults.withCredentials = true;

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/user');
      setUser(response.data.user);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    try {
      await axios.post('/api/logout');
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
      setUser(null); // Force logout on error
    }
  };

  if (loading) {
    return (
      <div className="App">
        <ThreeDScene />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      {/* Only show ThreeJS and floating elements when user is logged in */}
      {user && (
        <>
          <ThreeDScene />
          <div className="floating-elements">
            <div className="floating-icon pen-icon">✏️</div>
            <div className="floating-icon paper-icon">📄</div>
            <div className="floating-icon graph-icon">📊</div>
            <div className="floating-icon tick-icon">✅</div>
            <div className="floating-icon script-icon">📝</div>
          </div>
        </>
      )}
      
      <div className="app-content">
        <Router>
          {user ? (
            <div className="main-layout">
              <Sidebar user={user} onLogout={handleLogout} />
              <div className="main-content">
                <Routes>
                  <Route path="/dashboard" element={<Dashboard user={user} />} />
                  <Route path="/match" element={<SkillMatcherDashboard user={user} onLogout={handleLogout} />} />
                  <Route path="/history" element={<History user={user} />} />
                  <Route path="/result/:id" element={<ResultDetailsPage user={user} />} />
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </div>
            </div>
          ) : (
            <Routes>
              <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          )}
        </Router>
      </div>
    </div>
  );
}

export default App;