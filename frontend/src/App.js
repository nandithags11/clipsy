import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import VideoPage from './pages/VideoPage';
import './App.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check if user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner-large"></div>
        <p>Loading Clipsy...</p>
      </div>
    );
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route
            path="/login"
            element={
              isAuthenticated ? (
                <Navigate to="/videos" replace />
              ) : (
                <Login setIsAuthenticated={setIsAuthenticated} />
              )
            }
          />
          <Route
            path="/videos"
            element={
              isAuthenticated ? (
                <VideoPage setIsAuthenticated={setIsAuthenticated} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route path="/" element={<Navigate to="/videos" replace />} />
          <Route path="*" element={<Navigate to="/videos" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;