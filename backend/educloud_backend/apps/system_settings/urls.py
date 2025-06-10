from django.urls import path
from . import views

app_name = 'system_settings'

urlpatterns = [
    path('system/', views.system_settings, name='system_settings'),
]
