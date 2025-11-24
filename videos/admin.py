from django.contrib import admin
from .models import Video

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'duration', 'upload_date']
    list_filter = ['uploaded_date', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by')
        }),
        ('Files', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('duration', 'views', 'uploaded_date')
        }),
    )