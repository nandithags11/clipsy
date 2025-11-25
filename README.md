# Clipsy - Video Streaming Platform

Built with Django REST Framework and React, featuring automatic video transcoding to multiple quality levels and asynchronous processing with Celery.


## Architecture Overview

### System Design

Clipsy is a microservices-based video streaming platform that automatically processes uploaded videos into multiple quality levels for adaptive streaming.

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Browser   │◄───────►│    Nginx     │◄───────►│   Backend   │
│  (React)    │         │  (Frontend)  │         │  (Django)   │
└─────────────┘         └──────────────┘         └──────┬──────┘
                                                         │
                        ┌────────────────────────────────┼───────┐
                        │                                │       │
                   ┌────▼────┐                    ┌──────▼──────┐│
                   │  Redis  │◄───────────────────│   Celery    ││
                   │(Broker) │                    │   Worker    ││
                   └─────────┘                    └─────────────┘│
                        ▲                                        │
                        │                                        │
                   ┌────▼────┐                                   │
                   │Postgres │◄──────────────────────────────────┘
                   │   DB    │
                   └─────────┘
```

### Key Components

1. **Frontend (React + Nginx)**
   - Single-page application built with React
   - HLS video player with adaptive bitrate streaming
   - JWT-based authentication
   - Served via Nginx with API proxy configuration

2. **Backend (Django + Gunicorn)**
   - RESTful API built with Django REST Framework
   - JWT authentication using SimpleJWT
   - Video metadata management
   - Media file serving
   - PostgreSQL database integration

3. **Celery Worker**
   - Asynchronous video processing
   - FFmpeg integration for transcoding
   - Generates 4 quality levels: 360p, 480p, 720p, 1080p
   - Creates HLS segments and playlists
   - Thumbnail extraction

4. **PostgreSQL Database**
   - Stores video metadata
   - User authentication data
   - Video quality and segment information
   - Processing status tracking

5. **Redis**
   - Message broker for Celery
   - Task queue management
   - Result backend storage

### Technology Stack

**Backend:**
- Django 4.2.7
- Django REST Framework 3.14.0
- Gunicorn 21.2.0
- PostgreSQL (psycopg2-binary)
- Celery 5.3.4
- Redis 5.0.1
- FFmpeg

**Frontend:**
- React 18.2.0
- React Router 6.20.0
- Axios 1.6.2
- HLS.js 1.4.12
- Nginx (Alpine)

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- 2GB+ available disk space
- Ports 80, 8000, 5432, 6379 available

### One-Command Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd clipsy
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Start all services:
```bash
docker compose up --build
```

4. Access the application:
   - **Frontend**: http://localhost
   - **Backend API**: http://localhost:8000/api
   - **Django Admin**: http://localhost:8000/admin

### Default Credentials

- **Admin User**: `admin` / `admin123` (created automatically)
- **Test User**: Use Django admin to create additional users

### Stopping Services

```bash
docker compose down
```

To remove all data (including database):
```bash
docker compose down -v
```

---

## API Documentation

### Base URL

```
http://localhost/api
```

All API endpoints require the `/api` prefix. The frontend Nginx proxy automatically routes these requests to the Django backend.

### Authentication

Clipsy uses JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

### API Endpoints

#### 1. Authentication

##### Login
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "No active account found with the given credentials"
}
```

---

##### Logout
```http
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "detail": "Successfully logged out"
}
```

---

#### 2. Videos

##### List All Videos
```http
GET /api/videos/
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "title": "Sample Video",
    "description": "A sample video description",
    "thumbnail": "/media/videos/thumbnails/sample_thumb.jpg",
    "duration": 120.5,
    "views": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "status": "ready",
    "hls_playlist": "/media/videos/processed/1/master.m3u8",
    "qualities": [
      {
        "id": 1,
        "quality": "1080p",
        "resolution": "1920x1080",
        "bitrate": 5000,
        "file_size": 15728640,
        "playlist_path": "/media/videos/processed/1/1080p/playlist.m3u8"
      },
      {
        "id": 2,
        "quality": "720p",
        "resolution": "1280x720",
        "bitrate": 2500,
        "file_size": 7864320,
        "playlist_path": "/media/videos/processed/1/720p/playlist.m3u8"
      }
    ]
  }
]
```

---

##### Get Single Video
```http
GET /api/videos/{id}/
```

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Sample Video",
  "description": "Detailed description",
  "thumbnail": "/media/videos/thumbnails/sample_thumb.jpg",
  "duration": 120.5,
  "resolution": "1920x1080",
  "fps": 30,
  "views": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "status": "ready",
  "hls_playlist": "/media/videos/processed/1/master.m3u8",
  "qualities": [...]
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

##### Upload Video
```http
POST /api/videos/
```

**Request (multipart/form-data):**
```
title: "New Video"
description: "Video description"
video_file: <binary file data>
```

**Response (201 Created):**
```json
{
  "id": 2,
  "title": "New Video",
  "description": "Video description",
  "status": "processing",
  "created_at": "2024-01-15T11:00:00Z",
  "message": "Video uploaded successfully. Processing will begin shortly."
}
```

**Error Response (400 Bad Request):**
```json
{
  "video_file": ["This field is required."]
}
```

---

##### Stream Video
```http
GET /api/videos/{id}/stream/
```

**Response:**
- Returns the original video file as a binary stream
- Content-Type: video/mp4 (or appropriate video type)
- Supports range requests for seeking

---

### Video Processing Flow

1. **Upload**: Client uploads video via POST /api/videos/
2. **Storage**: Original video saved to `/media/videos/originals/`
3. **Status**: Video status set to "processing"
4. **Celery Task**: Background worker picks up the task
5. **Transcoding**: FFmpeg generates 4 quality versions
6. **HLS Creation**: Video segmented into 10-second chunks
7. **Playlist**: Master playlist created with all qualities
8. **Thumbnail**: Extracted at 1-second mark
9. **Complete**: Status updated to "ready"
10. **Streaming**: Client fetches master.m3u8 and plays via HLS.js

---

### Video Status Values

- `pending`: Uploaded, waiting for processing
- `processing`: Currently being transcoded
- `ready`: Processing complete, ready to stream
- `failed`: Processing encountered an error

---

### Error Handling

All API errors follow this format:

```json
{
  "detail": "Error message description"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message for this field"],
  "another_field": ["Another error message"]
}
```

## Development

### Local Development (Without Docker)

1. **Backend Setup:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

2. **Start Celery Worker:**
```bash
celery -A core worker --loglevel=info
```

3. **Frontend Setup:**
```bash
cd frontend
npm install
npm start
```

4. **Services:**
   - Install PostgreSQL and Redis locally
   - Update `.env` with `DB_HOST=localhost`

### Running Tests

```bash
# Backend tests
docker compose exec backend python manage.py test

# Or without Docker
python manage.py test
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery_worker
```

### Database Access

```bash
# Access PostgreSQL shell
docker compose exec db psql -U videostream_user -d videostream_db

# Or run migrations
docker compose exec backend python manage.py migrate
```

### Creating Django Admin User

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## Assumptions

### Technical Assumptions

1. **FFmpeg Availability**: Assumes FFmpeg is installed and accessible in the Docker container. The Dockerfile includes FFmpeg installation.

2. **Video Formats**: Assumes uploaded videos are in common formats supported by FFmpeg (MP4, AVI, MOV, etc.). No format validation is implemented.

3. **Storage**: Assumes sufficient disk space for storing both original and processed videos. Each video generates 4 quality versions plus HLS segments.

4. **Processing Time**: Video processing is asynchronous. Large videos may take several minutes to process. No progress tracking is implemented.

5. **Quality Levels**: Fixed quality levels (360p, 480p, 720p, 1080p) are generated regardless of source resolution. Lower source resolutions will not upscale.
