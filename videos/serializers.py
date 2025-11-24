from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    Video_url = serializers.StringRelatedField()  
    thumbnail_url = serializers.StringRelatedField()
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'upload_date', 'uploaded_by', 'video_file', 'thumbnail', 'duration']    
        read_only_fields = ['id', 'upload_date', 'uploaded_by']
        
    def get_video_url(self, obj):
        """Constructs full video file URL."""
        request = self.context.get('request')
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return None
    
    def get_thumbnail_url(self, obj):
        """Constructs full thumbnail URL."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None
    