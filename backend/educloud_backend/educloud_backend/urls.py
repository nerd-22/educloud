"""
URL configuration for educloud_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [    
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentications.urls')),
    path('api/schools/', include('apps.schools.urls')),
    path('api/settings/', include('apps.system_settings.urls')),
    path('api/school-details/', include('apps.schools_details.urls')),
    path('api/school-users/', include('apps.school_adding_users.urls')),
    path('api/', include('apps.school_analytics.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
