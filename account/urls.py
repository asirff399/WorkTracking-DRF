from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserRegisterAPIView, UserLoginAPIView, activate, UserLogoutAPIView, UserViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewset)

urlpatterns = [
    path('', include(router.urls)),
    path('register', UserRegisterAPIView.as_view(), name='register'),
    path('login', UserLoginAPIView.as_view(), name='login'),
    path('logout', UserLogoutAPIView.as_view(), name='logout'),
    path('activate/<uid64>/<token>/', activate, name='activate'),
    
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
]