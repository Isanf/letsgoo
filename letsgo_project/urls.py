from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Viral Video Admin Panel"
admin.site.site_title = "Viral Video Admin Portal"
admin.site.index_title = "Welcome to Video Viral!"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('letsgo.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)