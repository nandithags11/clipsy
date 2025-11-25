from celery import shared_task
from .video_processor import VideoProcessor
from .models import Video

@shared_task(bind=True)
def process_video(self, video_id):
    """Celery task to process video"""
    try:
        processor = VideoProcessor(video_id)
        result = processor.process()
        
        if result:
            return f"Video {video_id} processed successfully"
        else:
            return f"Video {video_id} processing failed"
            
    except Exception as e:
        video = Video.objects.get(id=video_id)
        video.status = 'failed'
        video.error_message = str(e)
        video.save()
        raise