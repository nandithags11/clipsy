"""
Test video processor without Celery
Run: python test_processor.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from videos.models import Video
from videos.video_processor import VideoProcessor
from django.contrib.auth.models import User

def test_processor():
    print("🎬 Testing Video Processor\n")
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing user: {user.username}")
    
    # Create video entry
    video = Video.objects.create(
        title='Test Video - Processor Test',
        description='Testing video processing pipeline',
        uploaded_by=user,
        original_file='videos/originals/test.mp4',
        status='pending'
    )
    
    print(f"\n📹 Created video entry:")
    print(f"   ID: {video.id}")
    print(f"   Title: {video.title}")
    print(f"   Status: {video.status}")
    print(f"   File: {video.original_file}")
    
    # Test if file exists
    file_path = os.path.join('media', str(video.original_file))
    if not os.path.exists(file_path):
        print(f"\nError: File not found at {file_path}")
        print("   Please download test video first:")
        print("   curl -o media/videos/originals/test.mp4 \\")
        print('     "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4"')
        return
    
    print(f" File exists: {file_path}")
    
    # Initialize processor
    print(f"\n🔧 Initializing video processor...")
    try:
        processor = VideoProcessor(video.id)
        print("Processor initialized")
    except Exception as e:
        print(f"Processor initialization failed: {e}")
        return
    
    # Test metadata extraction
    print(f"\nStep 1: Extracting metadata...")
    try:
        if processor.extract_metadata():
            video.refresh_from_db()
            print(f"   Metadata extracted:")
            print(f"   Duration: {video.duration}s")
            print(f"   Resolution: {video.width}x{video.height}")
            print(f"   FPS: {video.fps}")
        else:
            print(" Metadata extraction failed")
            return
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Test thumbnail generation
    print(f"\n  Step 2: Generating thumbnail...")
    try:
        if processor.generate_thumbnail():
            video.refresh_from_db()
            print(f" Thumbnail generated: {video.thumbnail}")
        else:
            print("  Thumbnail generation failed (non-critical)")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Test HLS creation for one quality
    print(f"\n📹 Step 3: Creating HLS stream (360p only for quick test)...")
    try:
        if processor.create_hls_stream('360p'):
            print(f" HLS stream created for 360p")
            
            # Check output files
            output_dir = processor.output_dir
            quality_dir = os.path.join(output_dir, '360p')
            
            if os.path.exists(quality_dir):
                files = os.listdir(quality_dir)
                print(f"   Generated files: {len(files)}")
                print(f"   Playlist: {os.path.exists(os.path.join(quality_dir, 'playlist.m3u8'))}")
                ts_files = [f for f in files if f.endswith('.ts')]
                print(f"   Segments: {len(ts_files)}")
        else:
            print(" HLS stream creation failed")
            return
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test master playlist
    print(f"\n Step 4: Creating master playlist...")
    try:
        if processor.create_master_playlist():
            video.refresh_from_db()
            print(f" Master playlist created: {video.hls_playlist}")
        else:
            print(" Master playlist creation failed")
            return
    except Exception as e:
        print(f" Error: {e}")
        return
    
    # Final status
    video.refresh_from_db()
    print(f"\n" + "="*50)
    print(f"PROCESSING TEST COMPLETE!")
    print(f"="*50)
    print(f"Video ID: {video.id}")
    print(f"Status: {video.status}")
    print(f"HLS URL: /media/{video.hls_playlist}")
    print(f"Thumbnail: /media/{video.thumbnail}")
    print(f"\nTo watch: http://127.0.0.1:8000/media/{video.hls_playlist}")
    print("="*50)

if __name__ == '__main__':
    test_processor()