from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from videos.models import Video
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates test user and sample video data'

    def handle(self, *args, **kwargs):
        # Create test user
        username = 'testuser'
        password = 'testpass123'
        email = 'test@example.com'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Test user created: {username}/{password}')
            )
        else:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.WARNING(f'⚠ Test user already exists: {username}')
            )
        
        # Create sample video entries
        sample_videos = [
            {
                'title': 'Sample Video 1',
                'description': 'First sample video for testing autoplay',
                'duration': 120,
            },
            {
                'title': 'Sample Video 2',
                'description': 'Second sample video for testing video switching',
                'duration': 180,
            },
            {
                'title': 'Sample Video 3',
                'description': 'Third sample video for testing the platform',
                'duration': 160,
            },
        ]
        
        for video_data in sample_videos:
            video, created = Video.objects.get_or_create(
                title=video_data['title'],
                defaults={
                    'description': video_data['description'],
                    'duration': video_data['duration'],
                    'uploaded_by': user,
                    'status': 'pending'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {video.title}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Test data setup complete!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'\n📝 Login credentials:')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Username: {username}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Password: {password}')
        )

