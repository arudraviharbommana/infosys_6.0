// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/LoginPage.jsx';
import SkillMatcherDashboard from './components/SkillMatcherDashboard.jsx';

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <Router>
            <div className="app">
                <Routes>
                    <Route 
                        path="/" 
                        element={
                            isAuthenticated ? 
                            <Navigate to="/dashboard" /> : 
                            <LoginPage setIsAuthenticated={setIsAuthenticated} />
                        } 
                    />
                    <Route 
                        path="/dashboard" 
                        element={
                            isAuthenticated ? 
                            <SkillMatcherDashboard setIsAuthenticated={setIsAuthenticated} /> : 
                            <Navigate to="/" />
                        } 
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;