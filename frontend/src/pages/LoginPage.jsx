import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../services/api';
import './LoginPage.css';

function LoginPage() {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true);
    const [showForgotPassword, setShowForgotPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setError('');
        setSuccess('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!formData.email || !formData.password) {
            setError('Please enter email and password');
            return;
        }

        if (!isLogin) {
            if (!formData.name) {
                setError('Please enter your name');
                return;
            }
            if (formData.password !== formData.confirmPassword) {
                setError('Passwords do not match');
                return;
            }
            if (formData.password.length < 6) {
                setError('Password must be at least 6 characters');
                return;
            }
        }

        setLoading(true);
        setError('');

        try {
            let result;
            if (isLogin) {
                result = await authApi.login(formData.email, formData.password);
            } else {
                result = await authApi.register(formData.name, formData.email, formData.password);
            }

            if (result.ok) {
                navigate('/');
            } else {
                setError(result.data.error || 'Authentication failed. Please try again.');
            }
        } catch (err) {
            setError('Connection error. Please check your network.');
        } finally {
            setLoading(false);
        }
    };

    const handleForgotPassword = (e) => {
        e.preventDefault();
        if (!formData.email) {
            setError('Please enter your email address first');
            return;
        }
        setShowForgotPassword(true);
        setSuccess(`Password reset link sent to ${formData.email}. Please check your inbox.`);
        setError('');
    };

    const switchMode = (e) => {
        e.preventDefault();
        setIsLogin(!isLogin);
        setError('');
        setSuccess('');
        setShowForgotPassword(false);
    };

    return (
        <div className="login-page">
            {/* Animated Background */}
            <div className="login-bg">
                <div className="bg-circle circle-1"></div>
                <div className="bg-circle circle-2"></div>
                <div className="bg-circle circle-3"></div>
            </div>

            {/* Login Card */}
            <div className="login-card animate-slideUp">
                {/* Logo */}
                <div className="login-logo">
                    <div className="logo-icon-wrapper">
                        <svg className="logo-icon-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 4C12 4 14.5 9 19 9C21.5 9 22.5 7.5 22.5 7.5C22.5 7.5 21.5 18 19 18C14.5 18 12 13 12 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M12 4C12 4 9.5 9 5 9C2.5 9 1.5 7.5 1.5 7.5C1.5 7.5 2.5 18 5 18C9.5 18 12 13 12 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M12 13V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <span className="logo-text">STUDY PILOT</span>
                    <span className="logo-badge">AI</span>
                </div>

                <h2 className="login-title">
                    {isLogin ? 'Welcome Back!' : 'Create Account'}
                </h2>
                <p className="login-subtitle">
                    {isLogin ? 'Sign in to continue your learning journey' : 'Join us to start your personalized learning'}
                </p>

                <form onSubmit={handleSubmit} className="login-form">
                    {!isLogin && (
                        <div className="input-group animate-fadeIn">
                            <span className="input-icon">👤</span>
                            <input
                                type="text"
                                name="name"
                                className="login-input"
                                placeholder="Full Name"
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </div>
                    )}

                    <div className="input-group">
                        <span className="input-icon">📧</span>
                        <input
                            type="email"
                            name="email"
                            className="login-input"
                            placeholder="Email Address"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <span className="input-icon">🔒</span>
                        <input
                            type="password"
                            name="password"
                            className="login-input"
                            placeholder="Password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    {!isLogin && (
                        <div className="input-group animate-fadeIn">
                            <span className="input-icon">🔐</span>
                            <input
                                type="password"
                                name="confirmPassword"
                                className="login-input"
                                placeholder="Confirm Password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                            />
                        </div>
                    )}

                    {error && (
                        <div className="login-error animate-shake">
                            <span>⚠️</span> {error}
                        </div>
                    )}

                    {success && (
                        <div className="login-success animate-fadeIn">
                            <span>✅</span> {success}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="login-btn"
                        disabled={loading}
                    >
                        {loading ? (
                            <span className="btn-loading">
                                <span className="spinner"></span>
                                Please wait...
                            </span>
                        ) : (
                            isLogin ? 'Sign In' : 'Create Account'
                        )}
                    </button>
                </form>

                <div className="login-footer">
                    {isLogin && (
                        <a href="#" className="footer-link" onClick={handleForgotPassword}>
                            Forgot Password?
                        </a>
                    )}
                    <a href="#" className="footer-link primary" onClick={switchMode}>
                        {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In"}
                    </a>
                </div>
            </div>

            {/* Page Footer */}
            <div className="page-footer">
                2026 © Study Pilot AI - Personalized Learning Platform
            </div>
        </div>
    );
}

export default LoginPage;
