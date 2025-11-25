import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import './Login.css';

function Login({ setIsAuthenticated }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);

      // Save tokens
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('username', response.data.username);

      // Update auth state
      setIsAuthenticated(true);

      // Redirect to videos
      navigate('/videos');
    } catch (err) {
      console.error('Login error:', err);
      setError(
        err.response?.data?.error || 'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  // Quick login with test credentials
  const handleQuickLogin = () => {
    setUsername('testuser');
    setPassword('testpass123');
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🎬 Clipsy</h1>
          <p className="tagline">Professional Video Streaming Platform</p>
          <p className="subtitle">Sign in to watch videos</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              autoComplete="username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️</span>
              {error}
            </div>
          )}

          <button type="submit" className="login-button" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-btn"></span>
                Signing in...
              </>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="test-credentials">
          <div className="credentials-header">
            <span className="info-icon">ℹ️</span>
            <strong>Test Credentials</strong>
          </div>
          <div className="credentials-content">
            <p>
              <span className="label">Username:</span> <code>testuser</code>
            </p>
            <p>
              <span className="label">Password:</span> <code>testpass123</code>
            </p>
          </div>
          <button onClick={handleQuickLogin} className="quick-login-btn">
            Quick Login
          </button>
        </div>

        <div className="features-list">
          <h4>✨ Features</h4>
          <ul>
            <li>🎬 Adaptive Bitrate Streaming (HLS)</li>
            <li>⚡ Multiple Playback Speeds (0.25x - 2x)</li>
            <li>📊 Quality Selection (360p - 1080p)</li>
            <li>🖼️ Picture-in-Picture Mode</li>
            <li>⌨️ Keyboard Shortcuts</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Login;