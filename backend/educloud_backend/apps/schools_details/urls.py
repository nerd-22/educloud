from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SchoolDetailsViewSet, PaymentSetupViewSet, FeeStructureViewSet,
    InvoiceViewSet, PaymentAlertViewSet, SchoolDocumentViewSet,
    CommunicationViewSet
)

router = DefaultRouter()
router.register(r'school-details', SchoolDetailsViewSet, basename='school-details')
router.register(r'payment-setups', PaymentSetupViewSet)
router.register(r'fee-structures', FeeStructureViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payment-alerts', PaymentAlertViewSet)
router.register(r'school-documents', SchoolDocumentViewSet)
router.register(r'communications', CommunicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]