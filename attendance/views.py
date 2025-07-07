from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import time

# Create your views here.
class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'employee'):
            return Attendance.objects.filter(employee=user.employee)
        return Attendance.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)
        
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_entry(self, request):
        employee = request.user.employee
        today = timezone.now().date()
        attendance, created = Attendance.objects.get_or_create(employee=employee, date=today)
        
        if attendance.entry_time:
            return Response({"message": "Entry already marked."}, status=400)
        
        attendance.entry_time = timezone.now().time()
        
        office_start = time(9, 0)
        if attendance.entry_time > office_start:
            attendance.is_late = True
        
        attendance.save()
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def mark_exit(self, request):
        employee = request.user.employee
        today = timezone.now().date()
        
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({"message": "Please mark entry first."}, status=400)
        
        if attendance.exit_time:
            return Response({"message": "Exit already marked."}, status=400)
        
        attendance.exit_time = timezone.now().time()
        attendance.calculate_total_hours()
        attendance.save()
        
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data)