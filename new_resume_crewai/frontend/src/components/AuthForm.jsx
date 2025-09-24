// src/components/AuthForm.jsx
import React, { useState } from 'react';

const AuthForm = ({ isLogin, onAuthSuccess }) => {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        name: ''
    });
    const [errors, setErrors] = useState({});
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!formData.email.includes('@')) {
            newErrors.email = 'Email must contain @ symbol';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        }

        if (!isLogin) {
            if (!formData.name) {
                newErrors.name = 'Name is required';
            }
            if (formData.password !== formData.confirmPassword) {
                newErrors.confirmPassword = 'Passwords do not match';
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }

        setIsLoading(true);

        // Mock authentication - in a real app, you'd call your backend
        setTimeout(() => {
            if (isLogin) {
                // Accept any email with @ and any password
                if (formData.email.includes('@') && formData.password) {
                    onAuthSuccess();
                } else {
                    setErrors({ general: 'Please enter a valid email (with @) and password' });
                }
            } else {
                // For registration, just accept any valid format
                onAuthSuccess();
            }
            setIsLoading(false);
        }, 1000);
    };

    return (
        <form className="auth-form" onSubmit={handleSubmit}>
            <h2>{isLogin ? 'Login' : 'Create Account'}</h2>
            
            {errors.general && (
                <div className="error-message general-error">
                    {errors.general}
                </div>
            )}

            {!isLogin && (
                <div className="form-group">
                    <label htmlFor="name">Full Name</label>
                    <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        className={errors.name ? 'error' : ''}
                        placeholder="Enter your full name"
                    />
                    {errors.name && <span className="error-message">{errors.name}</span>}
                </div>
            )}

            <div className="form-group">
                <label htmlFor="email">Email Address</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className={errors.email ? 'error' : ''}
                    placeholder={isLogin ? "Enter any email with @" : "Enter your email"}
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
            </div>

            <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className={errors.password ? 'error' : ''}
                    placeholder={isLogin ? "Enter any password" : "Choose a password"}
                />
                {errors.password && <span className="error-message">{errors.password}</span>}
            </div>

            {!isLogin && (
                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        className={errors.confirmPassword ? 'error' : ''}
                        placeholder="Confirm your password"
                    />
                    {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
                </div>
            )}

            <button type="submit" className="auth-button" disabled={isLoading}>
                {isLoading ? 'Processing...' : (isLogin ? 'Login' : 'Create Account')}
            </button>

            {isLogin && (
                <div className="demo-credentials">
                    <p><strong>Quick Login:</strong></p>
                    <p>Use any email with @ symbol</p>
                    <p>Use any password</p>
                    <p><em>Example: user@test.com / mypassword</em></p>
                </div>
            )}
        </form>
    );
};

export default AuthForm;