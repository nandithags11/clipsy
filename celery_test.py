"""
Test Celery task
Run: python test_celery_task.py
"""

import os
import sys
import django
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from videos.models import Video
from videos.tasks import process_video
from django.contrib.auth.models import User

def test_celery_task():
    print("🎬 Testing Celery Video Processing Task\n")
    
    # Get user
    user = User.objects.get(username='testuser')
    
    # Create video entry
    video = Video.objects.create(
        title='Test Video - Celery Task',
        description='Testing async video processing',
        uploaded_by=user,
        original_file='videos/originals/test.mp4',
        status='pending'
    )
    
    print(f"📹 Created video: {video.title} (ID: {video.id})")
    print(f"📤 Sending task to Celery...")
    
    # Send task to Celery
    task = process_video.delay(video.id)
    
    print(f"✅ Task sent! Task ID: {task.id}")
    print(f"⏳ Waiting for processing...")
    
    # Monitor progress
    for i in range(60):  # Wait up to 60 seconds
        time.sleep(1)
        video.refresh_from_db()
        
        print(f"\rStatus: {video.status} | Progress: {video.processing_progress}%", end='')
        
        if video.status == 'ready':
            print(f"\n\n✅ Processing complete!")
            print(f"HLS URL: /media/{video.hls_playlist}")
            break
        elif video.status == 'failed':
            print(f"\n\n❌ Processing failed!")
            print(f"Error: {video.error_message}")
            break
    else:
        print(f"\n\n⏰ Timeout - check Celery worker logs")

if __name__ == '__main__':
    test_celery_task()