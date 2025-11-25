from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    video_url = serializers.SerializerMethodField()  # Changed from StringRelatedField
    thumbnail_url = serializers.SerializerMethodField()  # Changed from StringRelatedField
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'uploaded_at', 'uploaded_by', 'video_file', 'thumbnail', 'duration','video_url','thumbnail_url','views']    
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']
        
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
    