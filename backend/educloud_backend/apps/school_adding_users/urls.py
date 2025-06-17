from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolUserViewSet

router = DefaultRouter()
router.register(r'school-users', SchoolUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
