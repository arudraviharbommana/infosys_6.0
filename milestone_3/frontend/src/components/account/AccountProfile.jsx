import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AccountProfile = ({ user }) => {
    const [accountStats, setAccountStats] = useState({
        totalAnalyses: 0,
        averageScore: 0,
        bestScore: 0,
        accountCreated: '',
        lastActivity: ''
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAccountStats();
    }, []);

    const fetchAccountStats = async () => {
        try {
            const response = await axios.get('/api/analyses');
            const analyses = response.data.analyses;
            
            const totalAnalyses = analyses.length;
            const averageScore = totalAnalyses > 0 
                ? Math.round(analyses.reduce((sum, a) => sum + a.match_score, 0) / totalAnalyses)
                : 0;
            const bestScore = totalAnalyses > 0 
                ? Math.max(...analyses.map(a => a.match_score))
                : 0;
            const lastActivity = totalAnalyses > 0 
                ? analyses[0].created_at
                : null;

            setAccountStats({
                totalAnalyses,
                averageScore,
                bestScore,
                accountCreated: user.created_at || new Date().toISOString(),
                lastActivity
            });
        } catch (error) {
            setError('Failed to load account statistics');
            console.error('Error fetching account stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const getScoreColor = (score) => {
        if (score >= 80) return '#22c55e';
        if (score >= 60) return '#eab308';
        if (score >= 40) return '#f97316';
        return '#ef4444';
    };

    if (loading) {
        return (
            <div className="account-profile">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
                    <p>Loading account information...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="account-profile">
            <div className="profile-header">
                <div className="profile-avatar">
                    <div className="avatar-circle">
                        {user.email.charAt(0).toUpperCase()}
                    </div>
                </div>
                <div className="profile-info">
                    <h1>{user.email.split('@')[0]}</h1>
                    <p className="profile-email">{user.email}</p>
                    <p className="profile-since">Member since {formatDate(accountStats.accountCreated)}</p>
                </div>
            </div>

            {error && (
                <div className="error-message">
                    <span className="error-icon">⚠️</span>
                    <p>{error}</p>
                </div>
            )}

            <div className="account-stats">
                <h2>📊 Account Statistics</h2>
                <div className="stats-grid">
                    <div className="stat-card">
                        <div className="stat-icon">📁</div>
                        <div className="stat-content">
                            <h3>Total Analyses</h3>
                            <div className="stat-value">{accountStats.totalAnalyses}</div>
                            <p className="stat-description">Skill matching analyses completed</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">📈</div>
                        <div className="stat-content">
                            <h3>Average Score</h3>
                            <div 
                                className="stat-value"
                                style={{ color: getScoreColor(accountStats.averageScore) }}
                            >
                                {accountStats.averageScore}%
                            </div>
                            <p className="stat-description">Average matching percentage</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🏆</div>
                        <div className="stat-content">
                            <h3>Best Score</h3>
                            <div 
                                className="stat-value"
                                style={{ color: getScoreColor(accountStats.bestScore) }}
                            >
                                {accountStats.bestScore}%
                            </div>
                            <p className="stat-description">Highest matching score achieved</p>
                        </div>
                    </div>

                    <div className="stat-card">
                        <div className="stat-icon">🕒</div>
                        <div className="stat-content">
                            <h3>Last Activity</h3>
                            <div className="stat-value">
                                {accountStats.lastActivity ? formatDate(accountStats.lastActivity) : 'No activity'}
                            </div>
                            <p className="stat-description">Most recent analysis</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="account-achievements">
                <h2>🏅 Achievements</h2>
                <div className="achievements-grid">
                    <div className={`achievement ${accountStats.totalAnalyses >= 1 ? 'earned' : 'locked'}`}>
                        <div className="achievement-icon">🎯</div>
                        <div className="achievement-info">
                            <h3>First Match</h3>
                            <p>Complete your first skill analysis</p>
                        </div>
                    </div>

                    <div className={`achievement ${accountStats.totalAnalyses >= 5 ? 'earned' : 'locked'}`}>
                        <div className="achievement-icon">📊</div>
                        <div className="achievement-info">
                            <h3>Analyzer</h3>
                            <p>Complete 5 skill analyses</p>
                        </div>
                    </div>

                    <div className={`achievement ${accountStats.bestScore >= 80 ? 'earned' : 'locked'}`}>
                        <div className="achievement-icon">⭐</div>
                        <div className="achievement-info">
                            <h3>High Scorer</h3>
                            <p>Achieve 80%+ match score</p>
                        </div>
                    </div>

                    <div className={`achievement ${accountStats.totalAnalyses >= 10 ? 'earned' : 'locked'}`}>
                        <div className="achievement-icon">🚀</div>
                        <div className="achievement-info">
                            <h3>Expert User</h3>
                            <p>Complete 10 skill analyses</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="account-actions">
                <h2>⚙️ Account Actions</h2>
                <div className="actions-grid">
                    <button className="action-button export-data">
                        <span className="action-icon">📥</span>
                        <div className="action-content">
                            <h3>Export Data</h3>
                            <p>Download your analysis history</p>
                        </div>
                    </button>

                    <button className="action-button account-settings">
                        <span className="action-icon">⚙️</span>
                        <div className="action-content">
                            <h3>Account Settings</h3>
                            <p>Manage your preferences</p>
                        </div>
                    </button>

                    <button className="action-button delete-account">
                        <span className="action-icon">🗑️</span>
                        <div className="action-content">
                            <h3>Delete Account</h3>
                            <p>Permanently remove your account</p>
                        </div>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AccountProfile;