import React from 'react';
import './VideoList.css';

function VideoList({ videos, currentVideoId, onVideoSelect, loading }) {
  if (loading) {
    return (
      <div className="video-list">
        <h3 className="list-title">Available Videos</h3>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading videos...</p>
        </div>
      </div>
    );
  }

  if (!videos || videos.length === 0) {
    return (
      <div className="video-list">
        <h3 className="list-title">Available Videos</h3>
        <div className="no-videos">
          <p>📹 No videos available</p>
          <small>Upload videos through Django admin</small>
        </div>
      </div>
    );
  }

  return (
    <div className="video-list">
      <h3 className="list-title">
        📺 Videos
        <span className="video-count">({videos.length})</span>
      </h3>

      <div className="video-grid">
        {videos.map((video) => (
          <div
            key={video.id}
            className={`video-card ${video.id === currentVideoId ? 'active' : ''} ${
              video.status !== 'ready' ? 'processing' : ''
            }`}
            onClick={() => video.status === 'ready' && onVideoSelect(video)}
          >
            <div className="thumbnail-wrapper">
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.title}
                  className="video-thumbnail"
                />
              ) : (
                <div className="no-thumbnail">
                  <span className="play-icon">▶️</span>
                </div>
              )}

              {video.duration && (
                <div className="duration-badge">
                  {Math.floor(video.duration / 60)}:
                  {(video.duration % 60).toString().padStart(2, '0')}
                </div>
              )}

              {video.status !== 'ready' && (
                <div className="processing-overlay">
                  <div className="processing-badge">
                    {video.status === 'processing' && (
                      <>
                        <div className="spinner-small"></div>
                        <span>{video.processing_progress}%</span>
                      </>
                    )}
                    {video.status === 'pending' && <span>⏳ Pending</span>}
                    {video.status === 'failed' && <span>❌ Failed</span>}
                  </div>
                </div>
              )}

              {video.id === currentVideoId && (
                <div className="now-playing-badge">▶ Now Playing</div>
              )}
            </div>

            <div className="video-card-info">
              <h4 className="video-card-title">{video.title}</h4>
              <div className="video-card-meta">
                <span className="video-views">👁️ {video.views} views</span>
                {video.qualities && video.qualities.length > 0 && (
                  <span className="video-quality">
                    📊 {video.qualities.length} qualities
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default VideoList;