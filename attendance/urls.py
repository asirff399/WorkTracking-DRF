from django.urls import path,include
from .views import AttendanceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'list', AttendanceViewSet, basename='attendance_list')

urlpatterns = [
    path('', include(router.urls)),
]
