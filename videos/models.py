from django.db import models
from django.contrib.auth.models import User
import os
#from djiango.utils import timezone
# Create your models here.

class Video(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    QUALITY_CHOICES = [
        ('360p', '360p'),
        ('480p', '480p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Original Video
    original_file = models.FileField(upload_to='videos/originals/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', null=True, blank=True)
    
    # Video Metadata
    duration = models.IntegerField(help_text="Duration in seconds", null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    fps = models.FloatField(null=True, blank=True)
    
    # Processing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processing_progress = models.IntegerField(default=0, help_text="Processing percentage")
    error_message = models.TextField(blank=True)
    
    # HLS Streaming
    hls_playlist = models.CharField(max_length=500, blank=True, help_text="Path to master.m3u8")
    
    # Analytics
    views = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_hls_url(self):
        """Get HLS playlist URL"""
        if self.hls_playlist:
            return f"/media/{self.hls_playlist}"
        return None


class VideoQuality(models.Model):
    """Stores different quality versions of a video"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='qualities')
    quality = models.CharField(max_length=10, choices=Video.QUALITY_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    bitrate = models.IntegerField(help_text="Bitrate in kbps")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['video', 'quality']
        ordering = ['quality']
    
    def __str__(self):
        return f"{self.video.title} - {self.quality}"


class VideoSegment(models.Model):
    """Stores HLS segments for a video quality"""
    quality = models.ForeignKey(VideoQuality, on_delete=models.CASCADE, related_name='segments')
    segment_number = models.IntegerField()
    file_path = models.CharField(max_length=500)
    duration = models.FloatField(help_text="Segment duration in seconds")
    
    class Meta:
        unique_together = ['quality', 'segment_number']
        ordering = ['segment_number']
    
    def __str__(self):
        return f"{self.quality} - Segment {self.segment_number}"