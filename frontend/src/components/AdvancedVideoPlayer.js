import React, { useRef, useEffect, useState } from 'react';
import Hls from 'hls.js';
import {
  FaPlay,
  FaPause,
  FaVolumeUp,
  FaVolumeMute,
  FaExpand,
  FaCompress,
  FaCog,
  FaTimes,
} from 'react-icons/fa';
import { MdPictureInPicture } from 'react-icons/md';
import './AdvancedVideoPlayer.css';

function AdvancedVideoPlayer({ hlsUrl, currentVideo }) {
  const videoRef = useRef(null);
  const hlsRef = useRef(null);
  const containerRef = useRef(null);

  // Player state
  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [muted, setMuted] = useState(false);
  const [buffered, setBuffered] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Settings state
  const [showSettings, setShowSettings] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const [quality, setQuality] = useState('auto');
  const [availableQualities, setAvailableQualities] = useState([]);

  // UI state
  const [showControls, setShowControls] = useState(true);
  const [controlsTimeout, setControlsTimeout] = useState(null);

  // Initialize HLS
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !hlsUrl) return;

    console.log('Loading HLS URL:', hlsUrl);

    // Native HLS support (Safari)
    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = hlsUrl;
      video.play().catch((e) => console.log('Autoplay prevented:', e));
    }
    // Use HLS.js for other browsers
    else if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        backBufferLength: 90,
      });

      hlsRef.current = hls;
      hls.loadSource(hlsUrl);
      hls.attachMedia(video);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        console.log('✅ HLS Manifest Parsed');

        // Get available quality levels
        const levels = hls.levels.map((level, index) => ({
          index,
          height: level.height,
          width: level.width,
          bitrate: level.bitrate,
          name: `${level.height}p`,
        }));

        setAvailableQualities(levels);
        console.log('Available qualities:', levels);

        // Auto-play
        video.play().catch((e) => console.log('Autoplay prevented:', e));
      });

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS Error:', data);
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              console.log('Network error, trying to recover...');
              hls.startLoad();
              break;
            case Hls.ErrorTypes.MEDIA_ERROR:
              console.log('Media error, trying to recover...');
              hls.recoverMediaError();
              break;
            default:
              console.log('Fatal error, cannot recover');
              hls.destroy();
              break;
          }
        }
      });

      return () => {
        if (hls) {
          hls.destroy();
        }
      };
    } else {
      console.error('HLS is not supported in this browser');
    }
  }, [hlsUrl]);

  // Video event handlers
  const handleTimeUpdate = () => {
    const video = videoRef.current;
    setCurrentTime(video.currentTime);
    setDuration(video.duration);

    // Update buffered
    if (video.buffered.length > 0) {
      const bufferedEnd = video.buffered.end(video.buffered.length - 1);
      const bufferedPercent = (bufferedEnd / video.duration) * 100;
      setBuffered(bufferedPercent);
    }
  };

  const handlePlayPause = () => {
    const video = videoRef.current;
    if (video.paused) {
      video.play();
      setPlaying(true);
    } else {
      video.pause();
      setPlaying(false);
    }
  };

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value);
    videoRef.current.currentTime = time;
    setCurrentTime(time);
  };

  const handleVolumeChange = (e) => {
    const vol = parseFloat(e.target.value);
    videoRef.current.volume = vol;
    setVolume(vol);
    setMuted(vol === 0);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    video.muted = !muted;
    setMuted(!muted);
    if (!muted) {
      setVolume(0);
    } else {
      setVolume(video.volume);
    }
  };

  const handlePlaybackRateChange = (rate) => {
    videoRef.current.playbackRate = rate;
    setPlaybackRate(rate);
    setShowSettings(false);
  };

  const handleQualityChange = (index) => {
    if (hlsRef.current) {
      if (index === -1) {
        hlsRef.current.currentLevel = -1; // Auto
        setQuality('auto');
      } else {
        hlsRef.current.currentLevel = index;
        const selectedQuality = availableQualities[index];
        setQuality(selectedQuality.name);
      }
    }
    setShowSettings(false);
  };

  const toggleFullscreen = async () => {
    const container = containerRef.current;

    try {
      if (!document.fullscreenElement) {
        await container.requestFullscreen();
        setIsFullscreen(true);
      } else {
        await document.exitFullscreen();
        setIsFullscreen(false);
      }
    } catch (error) {
      console.error('Fullscreen error:', error);
    }
  };

  const togglePictureInPicture = async () => {
    const video = videoRef.current;

    try {
      if (document.pictureInPictureElement) {
        await document.exitPictureInPicture();
      } else {
        await video.requestPictureInPicture();
      }
    } catch (error) {
      console.error('PiP error:', error);
      alert('Picture-in-Picture is not supported in your browser');
    }
  };

  // Auto-hide controls
  const handleMouseMove = () => {
    setShowControls(true);

    if (controlsTimeout) {
      clearTimeout(controlsTimeout);
    }

    const timeout = setTimeout(() => {
      if (playing) {
        setShowControls(false);
      }
    }, 3000);

    setControlsTimeout(timeout);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Don't trigger if typing in input
      if (e.target.tagName === 'INPUT') return;

      switch (e.key) {
        case ' ':
          e.preventDefault();
          handlePlayPause();
          break;
        case 'f':
          toggleFullscreen();
          break;
        case 'm':
          toggleMute();
          break;
        case 'ArrowLeft':
          videoRef.current.currentTime -= 5;
          break;
        case 'ArrowRight':
          videoRef.current.currentTime += 5;
          break;
        case 'ArrowUp':
          e.preventDefault();
          const newVolumeUp = Math.min(1, videoRef.current.volume + 0.1);
          videoRef.current.volume = newVolumeUp;
          setVolume(newVolumeUp);
          break;
        case 'ArrowDown':
          e.preventDefault();
          const newVolumeDown = Math.max(0, videoRef.current.volume - 0.1);
          videoRef.current.volume = newVolumeDown;
          setVolume(newVolumeDown);
          break;
        default:
          break;
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [playing]);

  const formatTime = (seconds) => {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!currentVideo) {
    return (
      <div className="no-video">
        <p>🎬 No video selected</p>
      </div>
    );
  }

  return (
    <div className="advanced-player-container">
      <div
        ref={containerRef}
        className="player-wrapper"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => playing && setShowControls(false)}
      >
        <video
          ref={videoRef}
          className="video-player"
          onTimeUpdate={handleTimeUpdate}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onClick={handlePlayPause}
        />

        {/* Loading Overlay */}
        {!playing && currentTime === 0 && (
          <div className="video-overlay">
            <div className="play-button-large" onClick={handlePlayPause}>
              <FaPlay />
            </div>
          </div>
        )}

        {/* Custom Controls */}
        <div className={`video-controls ${showControls ? 'visible' : ''}`}>
          {/* Progress Bar */}
          <div className="progress-container">
            <div className="progress-buffered" style={{ width: `${buffered}%` }} />
            <div
              className="progress-played"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
            <input
              type="range"
              min="0"
              max={duration || 0}
              value={currentTime}
              onChange={handleSeek}
              className="progress-input"
            />
          </div>

          <div className="controls-row">
            {/* Left Controls */}
            <div className="controls-left">
              <button onClick={handlePlayPause} className="control-btn" title="Play/Pause (Space)">
                {playing ? <FaPause /> : <FaPlay />}
              </button>

              <button onClick={toggleMute} className="control-btn" title="Mute (M)">
                {muted || volume === 0 ? <FaVolumeMute /> : <FaVolumeUp />}
              </button>

              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={muted ? 0 : volume}
                onChange={handleVolumeChange}
                className="volume-slider"
                title="Volume"
              />

              <span className="time-display">
                {formatTime(currentTime)} / {formatTime(duration)}
              </span>
            </div>

            {/* Right Controls */}
            <div className="controls-right">
              {/* Settings Button */}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`control-btn settings-btn ${showSettings ? 'active' : ''}`}
                title="Settings"
              >
                <FaCog />
              </button>

              {/* Picture in Picture */}
              <button 
                onClick={togglePictureInPicture} 
                className="control-btn"
                title="Picture in Picture"
              >
                <MdPictureInPicture />
              </button>

              {/* Fullscreen */}
              <button onClick={toggleFullscreen} className="control-btn" title="Fullscreen (F)">
                {isFullscreen ? <FaCompress /> : <FaExpand />}
              </button>
            </div>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="settings-panel">
            <div className="settings-header">
              <h3>⚙️ Settings</h3>
              <button
                onClick={() => setShowSettings(false)}
                className="settings-close"
              >
                <FaTimes />
              </button>
            </div>

            <div className="settings-body">
              {/* Playback Speed */}
              <div className="settings-section">
                <h4>⚡ Playback Speed</h4>
                <div className="settings-options">
                  {[0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2].map((rate) => (
                    <button
                      key={rate}
                      className={`settings-option ${
                        playbackRate === rate ? 'active' : ''
                      }`}
                      onClick={() => handlePlaybackRateChange(rate)}
                    >
                      {rate}x
                    </button>
                  ))}
                </div>
              </div>

              {/* Quality */}
              <div className="settings-section">
                <h4>📊 Quality</h4>
                <div className="settings-options">
                  <button
                    className={`settings-option ${
                      quality === 'auto' ? 'active' : ''
                    }`}
                    onClick={() => handleQualityChange(-1)}
                  >
                    Auto
                  </button>
                  {availableQualities.map((q, index) => (
                    <button
                      key={index}
                      className={`settings-option ${
                        quality === q.name ? 'active' : ''
                      }`}
                      onClick={() => handleQualityChange(index)}
                    >
                      {q.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Keyboard Shortcuts */}
              <div className="settings-section">
                <h4>⌨️ Keyboard Shortcuts</h4>
                <div className="shortcuts-list">
                  <div className="shortcut-item">
                    <kbd>Space</kbd>
                    <span>Play/Pause</span>
                  </div>
                  <div className="shortcut-item">
                    <kbd>F</kbd>
                    <span>Fullscreen</span>
                  </div>
                  <div className="shortcut-item">
                    <kbd>M</kbd>
                    <span>Mute</span>
                  </div>
                  <div className="shortcut-item">
                    <kbd>←/→</kbd>
                    <span>Seek ±5s</span>
                  </div>
                  <div className="shortcut-item">
                    <kbd>↑/↓</kbd>
                    <span>Volume ±10%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Video Info */}
      <div className="video-info-section">
        <h2 className="video-title">{currentVideo.title}</h2>
        <div className="video-meta">
          <span className="views">👁️ {currentVideo.views} views</span>
          {currentVideo.status && (
            <span className="status">
              📊 Status: <strong>{currentVideo.processing_status || currentVideo.status}</strong>
            </span>
          )}
          {currentVideo.duration && (
            <span className="duration">
              ⏱️ Duration: {Math.floor(currentVideo.duration / 60)}:
              {(currentVideo.duration % 60).toString().padStart(2, '0')}
            </span>
          )}
        </div>
        {currentVideo.description && (
          <div className="video-description">
            <p>{currentVideo.description}</p>
          </div>
        )}

        {/* Current Playback Info */}
        <div className="quality-info">
          <div className="info-item">
            <strong>Quality:</strong> {quality}
          </div>
          <div className="info-item">
            <strong>Speed:</strong> {playbackRate}x
          </div>
          {availableQualities.length > 0 && (
            <div className="info-item">
              <strong>Available:</strong> {availableQualities.map(q => q.name).join(', ')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default AdvancedVideoPlayer;