"""
    celery
"""


from celery import shared_task
from .video_processor import VideoProcessor
from .models import Video

@shared_task(bind=True)
def process_video(self, video_id):
    """
    Celery task to process video asynchronously
    
    Args:
        video_id: ID of the Video object to process
        
    Returns:
        str: Success or failure message
    """
    try:
        # Get video object
        video = Video.objects.get(id=video_id)
        
        # Log start
        print(f"🎬 Starting processing for video {video_id}: {video.title}")
        
        # Create processor
        processor = VideoProcessor(video_id)
        
        # Process video
        result = processor.process()
        
        if result:
            print(f"✅ Video {video_id} processed successfully")
            return f"Video {video_id} processed successfully"
        else:
            video.refresh_from_db()
            error_msg = video.error_message or "Unknown error"
            print(f"❌ Video {video_id} processing failed: {error_msg}")
            return f"Video {video_id} processing failed: {error_msg}"
            
    except Video.DoesNotExist:
        error_msg = f"Video {video_id} does not exist"
        print(f"❌ {error_msg}")
        return error_msg
        
    except Exception as e:
        error_msg = f"Error processing video {video_id}: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Update video status
        try:
            video = Video.objects.get(id=video_id)
            video.status = 'failed'
            video.error_message = str(e)
            video.save()
        except:
            pass
            
        raise