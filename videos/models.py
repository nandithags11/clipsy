from django.db import models
from django.contrib.auth.models import User
#from djiango.utils import timezone
# Create your models here.

class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return self.title
    
