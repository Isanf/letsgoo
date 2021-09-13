from django.contrib import admin
from .models import VideoPost, Comment, UserData

# Register your models here.
admin.site.register(VideoPost)
admin.site.register(Comment)
admin.site.register(UserData)