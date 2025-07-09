from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance
from .serializers import AttendanceSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import time
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

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
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def export_pdf(self, request):
        employee = request.user.employee
        start_date = parse_date(request.GET.get('start_date'))
        end_date = parse_date(request.GET.get('end_date'))
        
        if not start_date or not end_date:
            return Response({'error': 'Missing or invalid date range'},status=400)

        records = Attendance.objects.filter(employee=employee, date__range=(start_date,end_date)).order_by('date')
        
        html_string = render_to_string('pdf_report.html', {
            'records': records,
            'employee': employee,
            'start_date': start_date,
            'end_date': end_date,
        })
        
        html = HTML(string=html_string)
        pdf_file = html.write_pdf()
        
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
        return response