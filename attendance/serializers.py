from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'status', 'entry_time', 'exit_time', 'total_hours', 'is_late', 'is_early_leave']
        read_only_fields = ['total_hours', 'is_late', 'is_early_leave','date']
        
        