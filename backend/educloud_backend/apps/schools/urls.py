from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SchoolAdminViewSet

router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'school-admins', SchoolAdminViewSet, basename='school-admin')

# Custom routes for lookup by school code
urlpatterns = [
    path('schools/<str:school_code>/login/', SchoolViewSet.as_view({'post': 'school_login'}), name='school-login'),
    path('schools/<str:school_code>/dashboard/', SchoolViewSet.as_view({'get': 'dashboard'}), name='school-dashboard'),
    path('schools/<str:school_code>/public-info/', SchoolViewSet.as_view({'get': 'public_info'}), name='school-public-info'),
    path('', include(router.urls)),
]
