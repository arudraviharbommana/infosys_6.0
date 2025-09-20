import React, { useState } from 'react';
import ThreeDScene from './ThreeDScene';
import AuthForm from './AuthForm';
import '../styles/main.css';

const LoginPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);

  const handleAuthSubmit = (formData) => {
    // For demo purposes, just log the user in
    console.log('Auth data:', formData);
    
    // Simulate successful authentication
    const userData = {
      email: formData.email,
      isAuthenticated: true
    };
    
    onLogin(userData);
  };

  return (
    <div className="login-page">
      {/* 3D Background */}
      <ThreeDScene />
      
      {/* Content overlay */}
      <div className="content-overlay">
        <div className="brand-header">
          <h1 className="brand-title">SkillMatcher</h1>
          <p className="brand-subtitle">AI-Powered Resume Analysis & Career Guidance</p>
        </div>
        
        <AuthForm
          isLogin={isLogin}
          setIsLogin={setIsLogin}
          onSubmit={handleAuthSubmit}
        />
      </div>
    </div>
  );
};

export default LoginPage;