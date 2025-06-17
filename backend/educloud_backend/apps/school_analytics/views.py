from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.schools.models import School
from apps.authentications.auth import CustomTokenAuthentication
from django.utils import timezone
from datetime import timedelta

# Create your views here.

class SchoolAnalyticsViewSet(viewsets.ViewSet):
    authentication_classes = [CustomTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def analytics(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Get date range
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

            # Example analytics data - replace with actual queries
            analytics_data = {
                'attendance_rate': '85%',  # Replace with actual attendance calculation
                'performance_data': [
                    {'subject': 'Mathematics', 'average_score': 75},
                    {'subject': 'Science', 'average_score': 82},
                    {'subject': 'English', 'average_score': 78},
                    {'subject': 'History', 'average_score': 80},
                    {'subject': 'Geography', 'average_score': 77}
                ],
                'student_trends': {
                    'total_students': school.num_students,
                    'new_enrollments': 10,  # Replace with actual calculation
                    'withdrawals': 2  # Replace with actual calculation
                }
            }

            return Response(analytics_data)
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def notifications(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example notifications - replace with actual notifications from your database
            notifications = [
                {
                    'title': 'New Student Registration',
                    'message': 'A new student has registered for enrollment',
                    'time': '2 hours ago'
                },
                {
                    'title': 'System Update',
                    'message': 'System maintenance scheduled for tonight',
                    'time': '5 hours ago'
                }
            ]

            return Response({'notifications': notifications})
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def activities(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example activities - replace with actual activities from your database
            activities = [
                {
                    'action': 'New User Added',
                    'details': 'Added new teacher John Doe',
                    'time': '1 hour ago',
                    'status': 'Completed'
                },
                {
                    'action': 'System Update',
                    'details': 'Updated school settings',
                    'time': '3 hours ago',
                    'status': 'Completed'
                },
                {
                    'action': 'Student Enrollment',
                    'details': 'Processing new student registration',
                    'time': '5 hours ago',
                    'status': 'In Progress'
                }
            ]

            return Response({'activities': activities})
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def events(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example events - replace with actual events from your database
            events = [
                {
                    'title': 'Staff Meeting',
                    'date': 'Tomorrow at 10:00 AM',
                    'description': 'Monthly staff meeting in the conference room'
                },
                {
                    'title': 'End of Term',
                    'date': 'Next Week',
                    'description': 'End of current academic term'
                }
            ]

            return Response({'events': events})
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def messages(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example messages - replace with actual messages from your database
            messages = [
                {
                    'subject': 'Staff Training',
                    'sender': 'Admin',
                    'preview': 'Upcoming training session for new system features',
                    'time': '2h ago'
                },
                {
                    'subject': 'System Update',
                    'sender': 'System',
                    'preview': 'Important system updates scheduled',
                    'time': '5h ago'
                }
            ]

            return Response({'messages': messages})
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def financial(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example financial data - replace with actual data from your database
            financial_data = {
                'revenue': '$50,000',
                'expenses': '$30,000',
                'transactions': [
                    {
                        'category': 'Fees Collection',
                        'amount': '$15,000',
                        'status': 'Paid'
                    },
                    {
                        'category': 'Utilities',
                        'amount': '$2,000',
                        'status': 'Pending'
                    }
                ]
            }

            return Response(financial_data)
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def system_health(self, request, school_code=None):
        try:
            school = School.objects.get(school_code=school_code)
            
            # Example system health data - replace with actual monitoring data
            health_data = {
                'Database': {
                    'status': 'healthy',
                    'message': 'Operating normally'
                },
                'Storage': {
                    'status': 'warning',
                    'message': '75% utilized'
                },
                'Network': {
                    'status': 'healthy',
                    'message': 'All services up'
                },
                'Security': {
                    'status': 'healthy',
                    'message': 'Up to date'
                }
            }

            return Response(health_data)
        except School.DoesNotExist:
            return Response(
                {'error': 'School not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
