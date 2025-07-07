from django.db import models
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    entry_time = models.TimeField(null=True, blank=True)
    exit_time = models.TimeField(null=True, blank=True)
    total_hours = models.DurationField(null=True, blank=True)
    is_late = models.BooleanField(default=False)
    is_early_leave = models.BooleanField(default=False)
    
    def calculate_total_hours(self):
        if self.entry_time and self.exit_time:
            entry = timedelta(hours=self.entry_time.hour, minutes=self.entry_time.minute, seconds=self.entry_time.second)
            exit = timedelta(hours=self.exit_time.hour, minutes=self.exit_time.minute, seconds=self.exit_time.second)
            self.total_hours = exit - entry
            self.save()
            
            
    