from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.http import FileResponse
from .models import Video
from .serializers import VideoSerializer
# Create your views here.

class VideoViewSet(viewsets.ModelViewSet):
    
    
    """
    API end points
    1. GET /api/videos/ - List all videos
    2. POST /api/videos/ - Upload a new video
    3. GET /api/videos/{id}/stream/ - stream video file
    4. GET /api/videos/{id} - video details

    """
    
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def perform_upload(self, serializer):
        serializer.save(uploaded_by=self.request.user) # save video wirth logged in user

    @action(detail=True, methods=['get'])
    def stream(self, request, pk=None):
        """Streams the video file."""
        try:
            video =self.get_object()
            if not video.video_file:
                return Response({"detail": "Video file not found."}, status=status.HTTP_404_NOT_FOUND)
            
            Video_file = video.video_file.open('rb')
            response = FileResponse(Video_file, content_type='video/mp4')
            response['Accept-ranges'] ='bytes'
            return response
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list(self,request, *args, **kwargs):
        """List all videos."""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    def retrieve(self, request, *args, **kwargs):
        """Retrieve video details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)