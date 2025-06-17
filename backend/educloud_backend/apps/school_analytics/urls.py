from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolAnalyticsViewSet

router = DefaultRouter()
router.register(r'schools/(?P<school_code>[^/.]+)', SchoolAnalyticsViewSet, basename='school-analytics')

urlpatterns = [
    path('', include(router.urls)),
]