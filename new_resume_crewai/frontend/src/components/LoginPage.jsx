// src/components/LoginPage.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthForm from './AuthForm.jsx';

const LoginPage = ({ setIsAuthenticated }) => {
    const [isLogin, setIsLogin] = useState(true);
    const navigate = useNavigate();

    const handleAuthSuccess = () => {
        setIsAuthenticated(true);
        navigate('/dashboard');
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <div className="login-header">
                    <h1>AI-Free Skill Matcher</h1>
                    <p>Match your resume with job descriptions using advanced algorithms without AI dependency</p>
                </div>
                
                <AuthForm 
                    isLogin={isLogin} 
                    onAuthSuccess={handleAuthSuccess}
                />
                
                <div className="auth-toggle">
                    <p>
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <button 
                            className="link-button" 
                            onClick={() => setIsLogin(!isLogin)}
                        >
                            {isLogin ? 'Sign Up' : 'Login'}
                        </button>
                    </p>
                </div>
                
                <div className="features-preview">
                    <h3>Features:</h3>
                    <ul>
                        <li>✓ Rule-based skill extraction</li>
                        <li>✓ Comprehensive skill matching</li>
                        <li>✓ Learning path recommendations</li>
                        <li>✓ Interactive 3D visualization</li>
                        <li>✓ No AI dependencies</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;