from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from .models import Student, Attendance, Performance
from .serializers import UserSerializer, StudentSerializer, AttendanceSerializer, PerformanceSerializer


# Create your views here.
class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read methods for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Write permissions only for staff/teachers
        return request.user.is_authenticated and request.user.is_staff

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'class_name', 'admission_number']
    ordering_fields = ['name', 'enrollment_date', 'class_name']

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'status']
    ordering_fields = ['date', 'status']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get attendance summary data
        total_records = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='present').count()
        absent_count = Attendance.objects.filter(status='absent').count()
        late_count = Attendance.objects.filter(status='late').count()
        
        if total_records > 0:
            present_percent = (present_count / total_records) * 100
            absent_percent = (absent_count / total_records) * 100
            late_percent = (late_count / total_records) * 100
        else:
            present_percent = absent_percent = late_percent = 0
        
        return Response({
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'present_percent': round(present_percent, 2),
            'absent_percent': round(absent_percent, 2),
            'late_percent': round(late_percent, 2)
        })

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'subject']
    ordering_fields = ['date_recorded', 'score']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get performance summary data
        avg_score = Performance.objects.aggregate(avg_score=Avg('score'))['avg_score']
        
        # Get subject breakdown
        subjects = {}
        for subject in Performance.objects.values_list('subject', flat=True).distinct():
            subject_avg = Performance.objects.filter(subject=subject).aggregate(
                avg=Avg('score')
            )['avg']
            subjects[subject] = round(subject_avg, 2) if subject_avg else 0
        
        return Response({
            'overall_average': round(avg_score, 2) if avg_score else 0,
            'total_records': Performance.objects.count(),
            'subject_breakdown': subjects
        })
    
    # Add this function to the views.py file
    def home(request):
        return render(request, 'tracker/home.html')