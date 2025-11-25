import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdvancedVideoPlayer from '../components/AdvancedVideoPlayer';
import VideoList from '../components/VideoList';
import { videoAPI, authAPI } from '../services/api';
import './VideoPage.css';

function VideoPage({ setIsAuthenticated }) {
  const [videos, setVideos] = useState([]);
  const [currentVideo, setCurrentVideo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Load videos on mount
  useEffect(() => {
    loadVideos();
  }, []);

  const loadVideos = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await videoAPI.getVideos();
      const videoList = response.data;

      setVideos(videoList);

      // Auto-select first ready video
      const firstReadyVideo = videoList.find((v) => v.status === 'ready');
      if (firstReadyVideo) {
        setCurrentVideo(firstReadyVideo);
      }
    } catch (err) {
      console.error('Error loading videos:', err);
      setError('Failed to load videos. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleVideoSelect = (video) => {
    if (video.status === 'ready') {
      setCurrentVideo(video);
      // Scroll to top on mobile
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      setIsAuthenticated(false);
      navigate('/login');
    }
  };

  const handleRefresh = () => {
    loadVideos();
  };

  const username = localStorage.getItem('username');

  return (
    <div className="video-page">
      {/* Header */}
      <header className="page-header">
        <div className="header-left">
          <h1 className="logo">🎬 Clipsy</h1>
          <p className="tagline">Video Streaming Platform</p>
        </div>
        <div className="header-right">
          <button onClick={handleRefresh} className="refresh-btn" title="Refresh videos">
            🔄 Refresh
          </button>
          <div className="user-info">
            <span className="username">👤 {username}</span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="page-content">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
            <button onClick={loadVideos}>Retry</button>
          </div>
        )}

        <div className="content-grid">
          {/* Video Player */}
          <div className="player-section">
            {currentVideo && currentVideo.hls_url ? (
              <AdvancedVideoPlayer
                hlsUrl={currentVideo.hls_url}
                currentVideo={currentVideo}
              />
            ) : (
              <div className="no-video-selected">
                <div className="placeholder-content">
                  <div className="placeholder-icon">🎬</div>
                  <h2>Welcome to Clipsy!</h2>
                  <p>
                    {loading
                      ? 'Loading videos...'
                      : videos.length === 0
                      ? 'No videos available yet'
                      : 'Select a video from the list to start watching'}
                  </p>
                  {videos.length === 0 && !loading && (
                    <small>Upload videos through Django admin panel</small>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Video List */}
          <aside className="sidebar-section">
            <VideoList
              videos={videos}
              currentVideoId={currentVideo?.id}
              onVideoSelect={handleVideoSelect}
              loading={loading}
            />
          </aside>
        </div>
      </main>

      {/* Footer */}
      <footer className="page-footer">
        <p>
          Built with Django + React + HLS.js | Adaptive Bitrate Streaming | Multiple
          Quality Options
        </p>
      </footer>
    </div>
  );
}

export default VideoPage;