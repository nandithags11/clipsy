from django.contrib import admin
from .models import Video

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploaded_by', 'duration', 'upload_date','views']
    list_filter = ['upload_date', 'uploaded_by']
    search_fields = ['title', 'description']
    readonly_fields = ['upload_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'uploaded_by')
        }),
        ('Files', {
            'fields': ('video_file', 'thumbnail')
        }),
        ('Metadata', {
            'fields': ('duration', 'views', 'upload_date')
        }),
    )