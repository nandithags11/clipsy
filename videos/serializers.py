from rest_framework import serializers
from .models import Video, VideoQuality, VideoSegment

class VideoQualitySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoQuality
        fields = ['quality', 'file_path', 'file_size', 'bitrate']

class VideoSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()
    qualities = VideoQualitySerializer(many=True, read_only=True)
    hls_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    processing_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'uploaded_by', 'uploaded_at',
            'duration', 'width', 'height', 'fps',
            'status', 'processing_progress', 'error_message',
            'thumbnail', 'thumbnail_url',
            'hls_url', 'qualities', 'views',
            'processing_status'
        ]
        read_only_fields = ['uploaded_by', 'uploaded_at', 'views', 'status']
    
    def get_hls_url(self, obj):
        """Return HLS master playlist URL"""
        if obj.hls_playlist:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f'/media/{obj.hls_playlist}')
        return None
    
    def get_thumbnail_url(self, obj):
        """Return thumbnail URL"""
        if obj.thumbnail:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.thumbnail.url)
        return None
    
    def get_processing_status(self, obj):
        """Return user-friendly processing status"""
        status_map = {
            'pending': 'Waiting to process',
            'processing': f'Processing ({obj.processing_progress}%)',
            'ready': 'Ready to watch',
            'failed': 'Processing failed'
        }
        return status_map.get(obj.status, obj.status)

class VideoUploadSerializer(serializers.ModelSerializer):
    """Serializer for video upload"""
    
    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'original_file']
    
    def create(self, validated_data):
        # Set uploaded_by from request user
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)