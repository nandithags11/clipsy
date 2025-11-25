# videos/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video
from .video_processor import VideoProcessor 
import threading

def start_video_processing(video_id):
    """Function to run in a separate thread"""
    processor = VideoProcessor(video_id)
    processor.process()

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Triggered automatically when a Video is saved.
    Only runs if 'created' is True (new upload).
    """
    if created:
        # We run this in a thread so the Admin page doesn't freeze
        # while FFmpeg converts the video
        thread = threading.Thread(
            target=start_video_processing, 
            args=(instance.id,)
        )
        thread.start()