from django.contrib import admin
from .models import Video

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'duration', 'uploaded_at','views']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by')
        }),
        ('Files', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('duration', 'views', 'uploaded_at')
        }),
    )