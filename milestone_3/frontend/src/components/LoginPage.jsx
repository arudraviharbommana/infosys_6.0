import React, { useState } from 'react';
import axios from 'axios';
import AuthForm from './AuthForm';

const LoginPage = ({ onLogin }) => {
    const [currentView, setCurrentView] = useState('login');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (email, password) => {
        setLoading(true);
        setError('');
        
        try {
            const response = await axios.post('/api/login', {
                email,
                password
            });
            
            onLogin(response.data.user);
        } catch (error) {
            setError(error.response?.data?.error || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    const handleSignup = async (email, password) => {
        setLoading(true);
        setError('');
        
        try {
            const response = await axios.post('/api/register', {
                email,
                password
            });
            
            onLogin(response.data.user);
        } catch (error) {
            setError(error.response?.data?.error || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    const handleAuthSubmit = (email, password) => {
        if (currentView === 'login') {
            handleLogin(email, password);
        } else {
            handleSignup(email, password);
        }
    };

    return (
        <div className="login-page">
            {/* Skill-based floating elements - Left side */}
            <div className="login-floating-left">
                <div className="floating-element python-icon">🐍</div>
                <div className="floating-element database-icon">�️</div>
                <div className="floating-element torch-icon">🔦</div>
                <div className="floating-element cyber-icon">🛡️</div>
                <div className="floating-element flask-icon">⚗️</div>
                <div className="floating-element admin-icon">👨‍💼</div>
                <div className="floating-element language-icon">🌐</div>
                <div className="floating-element r-lang-icon">�</div>
                <div className="floating-element cpp-icon">⚙️</div>
                <div className="floating-element ai-icon">🤖</div>
                <div className="floating-element ml-icon">🧠</div>
                <div className="floating-element data-icon">📈</div>
                <div className="floating-element cloud-icon">☁️</div>
                <div className="floating-element web-icon">🌍</div>
                <div className="floating-element mobile-icon">📱</div>
            </div>
            
            {/* Skill-based floating elements - Right side */}
            <div className="login-floating-right">
                <div className="floating-element java-icon">☕</div>
                <div className="floating-element js-icon">�</div>
                <div className="floating-element react-icon">⚛️</div>
                <div className="floating-element node-icon">🟢</div>
                <div className="floating-element docker-icon">🐳</div>
                <div className="floating-element git-icon">🌳</div>
                <div className="floating-element analytics-icon">📊</div>
                <div className="floating-element security-icon">🔒</div>
                <div className="floating-element api-icon">🔗</div>
                <div className="floating-element blockchain-icon">⛓️</div>
                <div className="floating-element iot-icon">�</div>
                <div className="floating-element devops-icon">🔧</div>
                <div className="floating-element ui-icon">🎨</div>
                <div className="floating-element testing-icon">🧪</div>
                <div className="floating-element agile-icon">🏃‍♂️</div>
            </div>
            
            <div className="login-container">
                <div className="login-header">
                    <h1>AI Skill Matcher</h1>
                    <p>Comprehensive skill analysis and job matching platform</p>
                </div>
                
                <div className="auth-tabs">
                    <button 
                        className={currentView === 'login' ? 'active' : ''}
                        onClick={() => {
                            setCurrentView('login');
                            setError('');
                        }}
                    >
                        Sign In
                    </button>
                    <button 
                        className={currentView === 'signup' ? 'active' : ''}
                        onClick={() => {
                            setCurrentView('signup');
                            setError('');
                        }}
                    >
                        Create Account
                    </button>
                </div>

                {error && (
                    <div className="error-message">
                        {error}
                    </div>
                )}

                <AuthForm 
                    mode={currentView} 
                    onSubmit={handleAuthSubmit}
                    loading={loading}
                />
                
                <div className="features-preview">
                    <h3>Features</h3>
                    <ul>
                        <li>📊 Comprehensive skill analysis</li>
                        <li>🎯 Job matching with detailed insights</li>
                        <li>📈 Analysis history and tracking</li>
                        <li>💡 Personalized recommendations</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;