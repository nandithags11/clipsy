
# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Video

class VideoAdminTest(TestCase):
    def setUp(self):
        # 1. Create a superuser (admin) so we can log in
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            password='password123', 
            email='admin@test.com'
        )
        self.client = Client()
        self.client.login(username='admin', password='password123')

    def test_admin_add_video_page_loads(self):
        """
        Tests if the 'Add Video' page loads with status 200.
        If your admin.py has a field error, this test will FAIL (500 error).
        """
        # This generates the URL: /admin/videos/video/add/
        url = reverse('admin:videos_video_add') 
        
        response = self.client.get(url)
        
        # Check if we got a success response (200 OK)
        self.assertEqual(response.status_code, 200)

class VideoModelTest(TestCase):
    def test_create_video(self):
        """
        Tests if we can create a video object in the database.
        """
        # 1. Create a dummy user first (because a Video needs an uploader)
        user = User.objects.create_user(username='uploader', password='password')

        # 2. Create the video and assign the user to 'uploaded_by'
        video = Video.objects.create(
            title="My Test Video",
            uploaded_by=user  # <--- This fixes the error!
        )
        
        self.assertEqual(video.title, "My Test Video")