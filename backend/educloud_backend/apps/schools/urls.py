from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SchoolViewSet, SchoolAdminViewSet

router = DefaultRouter()
router.register(r'', SchoolViewSet, basename='school')
router.register(r'admins', SchoolAdminViewSet, basename='school-admin')

# Combined urlpatterns
urlpatterns = [
    # School admin specific routes
    path('admins/update-password/', SchoolAdminViewSet.as_view({'post': 'update_password'}), name='admin-update-password'),
    
    # School specific routes
    path('<str:school_code>/login/', SchoolViewSet.as_view({'post': 'school_login'}), name='school-login'),
    path('<str:school_code>/dashboard/', SchoolViewSet.as_view({'get': 'dashboard'}), name='school-dashboard'),
    path('<str:school_code>/public-info/', SchoolViewSet.as_view({'get': 'public_info'}), name='school-public-info'),
    path('<str:school_code>/administrators/', SchoolViewSet.as_view({'get': 'get_administrators'}), name='school-administrators'),
    path('<str:school_code>/invoices/', SchoolViewSet.as_view({'get': 'get_invoices'}), name='school-invoices'),
    path('<str:school_code>/communications/', SchoolViewSet.as_view({'get': 'get_communications'}), name='school-communications'),
    path('<str:school_code>/documents/', SchoolViewSet.as_view({'get': 'get_documents'}), name='school-documents'),
    path('<str:school_code>/toggle-status/', SchoolViewSet.as_view({'post': 'toggle_status'}), name='school-toggle-status'),
    path('<str:school_code>/reset-database/', SchoolViewSet.as_view({'post': 'reset_database'}), name='school-reset-database'),
    path('', include(router.urls)),
]
