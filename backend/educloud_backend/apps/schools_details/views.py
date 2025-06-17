from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.schools.models import School
from apps.schools.serializers import SchoolSerializer
from .models import (
    PaymentSetup, FeeStructure, Invoice, PaymentAlert,
    SchoolDocument, Communication, SchoolDetails
)
from .serializers import (
    PaymentSetupSerializer, FeeStructureSerializer, InvoiceSerializer,
    PaymentAlertSerializer, SchoolDocumentSerializer, CommunicationSerializer, SchoolDetailsSerializer
)
import logging

# Create your views here.

logger = logging.getLogger(__name__)

class SuperAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'is_super_admin') and request.user.is_super_admin

class SchoolDetailsPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'is_super_admin') and request.user.is_super_admin:
            return True
            
        if hasattr(request.user, 'is_school_admin') and request.user.is_school_admin:
            if view.action in ['retrieve', 'update', 'partial_update']:
                return True
        return False

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'is_super_admin') and request.user.is_super_admin:
            return True
            
        if hasattr(request.user, 'is_school_admin') and request.user.is_school_admin:
            return obj.school == request.user.school
        return False

class SchoolDetailsViewSet(viewsets.ModelViewSet):
    queryset = SchoolDetails.objects.all()
    serializer_class = SchoolDetailsSerializer
    permission_classes = [SchoolDetailsPermission]
    
    def get_queryset(self):
        logger.debug(f"User: {self.request.user}")
        if hasattr(self.request.user, 'is_super_admin') and self.request.user.is_super_admin:
            return SchoolDetails.objects.all()
        elif hasattr(self.request.user, 'is_school_admin') and self.request.user.is_school_admin:
            return SchoolDetails.objects.filter(school=self.request.user.school)
        return SchoolDetails.objects.none()
    
    def create(self, request, *args, **kwargs):
        if not request.data.get('school'):
            return Response(
                {"error": "School ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            school = School.objects.get(id=request.data['school'])
        except School.DoesNotExist:
            return Response(
                {"error": "School not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if details already exist
        if SchoolDetails.objects.filter(school=school).exists():
            return Response(
                {"error": "School details already exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """Get both school and its detailed information"""
        instance = self.get_object()
        data = self.get_serializer(instance).data
        # Add any additional computed fields or aggregated data here
        return Response(data)

    @action(detail=False, methods=['get'], url_path='school/(?P<school_code>[^/.]+)')
    def get_by_school(self, request, school_code=None):
        try:
            if not school_code:
                return Response(
                    {'error': 'School code is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            school = get_object_or_404(School, school_code=school_code)
            school_details = SchoolDetails.objects.filter(school=school).first()
            
            if not school_details:
                return Response(
                    {'error': f'No details found for school with code {school_code}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = SchoolDetailsSerializer(school_details)
            return Response(serializer.data)
            
        except School.DoesNotExist:
            return Response(
                {'error': f'School with code {school_code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error fetching school details: {str(e)}')
            return Response(
                {'error': 'An error occurred while fetching school details'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentSetupViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = PaymentSetupSerializer
    queryset = PaymentSetup.objects.all()

class FeeStructureViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = FeeStructureSerializer
    queryset = FeeStructure.objects.all()

class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()

class PaymentAlertViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = PaymentAlertSerializer
    queryset = PaymentAlert.objects.all()

class SchoolDocumentViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = SchoolDocumentSerializer
    queryset = SchoolDocument.objects.all()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

class CommunicationViewSet(viewsets.ModelViewSet):
    permission_classes = [SuperAdminPermission]
    serializer_class = CommunicationSerializer
    queryset = Communication.objects.all()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class SchoolDetailsViewSet(viewsets.ModelViewSet):
    queryset = SchoolDetails.objects.all()
    serializer_class = SchoolDetailsSerializer
    permission_classes = [SchoolDetailsPermission]
    
    def get_queryset(self):
        logger.debug(f"User: {self.request.user}")
        if hasattr(self.request.user, 'is_super_admin') and self.request.user.is_super_admin:
            return SchoolDetails.objects.all()
        elif hasattr(self.request.user, 'is_school_admin') and self.request.user.is_school_admin:
            return SchoolDetails.objects.filter(school=self.request.user.school)
        return SchoolDetails.objects.none()
    
    def create(self, request, *args, **kwargs):
        if not request.data.get('school'):
            return Response(
                {"error": "School ID is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            school = School.objects.get(id=request.data['school'])
        except School.DoesNotExist:
            return Response(
                {"error": "School not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Check if details already exist
        if SchoolDetails.objects.filter(school=school).exists():
            return Response(
                {"error": "School details already exist"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(school=school)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """Get both school and its detailed information"""
        instance = self.get_object()
        data = self.get_serializer(instance).data
        # Add any additional computed fields or aggregated data here
        return Response(data)

    @action(detail=False, methods=['get'], url_path='school/(?P<school_code>[^/.]+)')
    def get_by_school(self, request, school_code=None):
        try:
            if not school_code:
                return Response(
                    {'error': 'School code is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            school = get_object_or_404(School, school_code=school_code)
            school_details = SchoolDetails.objects.filter(school=school).first()
            
            if not school_details:
                return Response(
                    {'error': f'No details found for school with code {school_code}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = SchoolDetailsSerializer(school_details)
            return Response(serializer.data)
            
        except School.DoesNotExist:
            return Response(
                {'error': f'School with code {school_code} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error fetching school details: {str(e)}')
            return Response(
                {'error': 'An error occurred while fetching school details'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
