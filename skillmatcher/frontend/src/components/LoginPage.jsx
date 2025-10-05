
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ThreeDScene from './ThreeDScene';
import AuthForm from './AuthForm';
import '../styles/main.css';
import { API_BASE_URL } from '../config';

const LoginPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();

  const handleAuthSubmit = async (formData) => {
    try {
      const res = await fetch(`${API_BASE_URL}/user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password
        })
      });
      if (!res.ok) throw new Error('Login/Signup failed');
      const userData = await res.json();
      userData.isAuthenticated = true;
      onLogin(userData);
      navigate('/dashboard');
    } catch (err) {
      alert('Login/Signup failed: ' + err.message);
    }
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