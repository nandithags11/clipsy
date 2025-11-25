import os
import subprocess
import json
from pathlib import Path
from django.conf import settings
from .models import Video, VideoQuality, VideoSegment

class VideoProcessor:
    """Handles video processing with FFmpeg"""
    
    QUALITY_SETTINGS = {
        '360p': {'width': 640, 'height': 360, 'bitrate': '500k'},
        '480p': {'width': 854, 'height': 480, 'bitrate': '1000k'},
        '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
        '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
    }
    
    def __init__(self, video_id):
        self.video = Video.objects.get(id=video_id)
        self.input_path = self.video.original_file.path
        self.output_dir = os.path.join(
            settings.MEDIA_ROOT, 
            'videos', 
            'processed', 
            str(self.video.id)
        )
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_metadata(self):
        """Extract video metadata using FFprobe"""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            self.input_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            
            # Find video stream
            video_stream = next(
                (s for s in data['streams'] if s['codec_type'] == 'video'), 
                None
            )
            
            if video_stream:
                self.video.width = video_stream.get('width')
                self.video.height = video_stream.get('height')
                self.video.fps = eval(video_stream.get('r_frame_rate', '0/1'))
            
            # Get duration
            if 'format' in data:
                self.video.duration = int(float(data['format'].get('duration', 0)))
            
            self.video.save()
            return True
            
        except Exception as e:
            self.video.status = 'failed'
            self.video.error_message = f"Metadata extraction failed: {str(e)}"
            self.video.save()
            return False
    
    def generate_thumbnail(self):
        """Generate thumbnail from video"""
        thumbnail_path = os.path.join(
            settings.MEDIA_ROOT, 
            'videos', 
            'thumbnails', 
            f'{self.video.id}.jpg'
        )
        
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        cmd = [
            'ffmpeg',
            '-i', self.input_path,
            '-ss', '00:00:01',  # Take frame at 1 second
            '-vframes', '1',
            '-vf', 'scale=640:360',
            '-y',
            thumbnail_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            self.video.thumbnail = f'videos/thumbnails/{self.video.id}.jpg'
            self.video.save()
            return True
        except Exception as e:
            print(f"Thumbnail generation failed: {e}")
            return False
    
    def create_hls_stream(self, quality):
        """Create HLS stream for a specific quality"""
        settings_data = self.QUALITY_SETTINGS[quality]
        
        # Output directory for this quality
        quality_dir = os.path.join(self.output_dir, quality)
        os.makedirs(quality_dir, exist_ok=True)
        
        # Output files
        playlist_file = os.path.join(quality_dir, 'playlist.m3u8')
        segment_pattern = os.path.join(quality_dir, 'segment_%03d.ts')
        
        # FFmpeg command
        cmd = [
            'ffmpeg',
            '-i', self.input_path,
            '-vf', f"scale={settings_data['width']}:{settings_data['height']}",
            '-c:v', 'libx264',
            '-b:v', settings_data['bitrate'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-hls_time', '10',  # 10 second segments
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', segment_pattern,
            '-f', 'hls',
            '-y',
            playlist_file
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Save quality info
            file_size = sum(
                os.path.getsize(os.path.join(quality_dir, f))
                for f in os.listdir(quality_dir)
                if f.endswith('.ts')
            )
            
            quality_obj, created = VideoQuality.objects.update_or_create(
                video=self.video,
                quality=quality,
                defaults={
                    'file_path': f'videos/processed/{self.video.id}/{quality}/playlist.m3u8',
                    'file_size': file_size,
                    'bitrate': int(settings_data['bitrate'].replace('k', ''))
                }
            )
            
            # Save segment info
            segments = sorted([f for f in os.listdir(quality_dir) if f.endswith('.ts')])
            for i, segment in enumerate(segments):
                VideoSegment.objects.update_or_create(
                    quality=quality_obj,
                    segment_number=i,
                    defaults={
                        'file_path': f'videos/processed/{self.video.id}/{quality}/{segment}',
                        'duration': 10.0
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"HLS creation failed for {quality}: {e}")
            return False
    
    def create_master_playlist(self):
        """Create master HLS playlist with all qualities"""
        master_playlist = os.path.join(self.output_dir, 'master.m3u8')
        
        with open(master_playlist, 'w') as f:
            f.write('#EXTM3U\n')
            f.write('#EXT-X-VERSION:3\n\n')
            
            for quality in self.QUALITY_SETTINGS:
                if VideoQuality.objects.filter(video=self.video, quality=quality).exists():
                    settings_data = self.QUALITY_SETTINGS[quality]
                    bandwidth = int(settings_data['bitrate'].replace('k', '')) * 1000
                    
                    f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},'
                           f'RESOLUTION={settings_data["width"]}x{settings_data["height"]}\n')
                    f.write(f'{quality}/playlist.m3u8\n')
        
        self.video.hls_playlist = f'videos/processed/{self.video.id}/master.m3u8'
        self.video.save()
        
        return True
    
    def process(self):
        """Main processing pipeline"""
        try:
            # Update status
            self.video.status = 'processing'
            self.video.processing_progress = 0
            self.video.save()
            
            # Step 1: Extract metadata (10%)
            if not self.extract_metadata():
                return False
            self.video.processing_progress = 10
            self.video.save()
            
            # Step 2: Generate thumbnail (20%)
            self.generate_thumbnail()
            self.video.processing_progress = 20
            self.video.save()
            
            # Step 3: Create HLS streams for each quality (70%)
            qualities = ['360p', '480p', '720p', '1080p']
            progress_per_quality = 70 / len(qualities)
            
            for i, quality in enumerate(qualities):
                if self.create_hls_stream(quality):
                    self.video.processing_progress = 20 + int((i + 1) * progress_per_quality)
                    self.video.save()
            
            # Step 4: Create master playlist (90%)
            self.create_master_playlist()
            self.video.processing_progress = 90
            self.video.save()
            
            # Done!
            self.video.status = 'ready'
            self.video.processing_progress = 100
            self.video.save()
            
            return True
            
        except Exception as e:
            self.video.status = 'failed'
            self.video.error_message = str(e)
            self.video.processing_progress = 0
            self.video.save()
            return False