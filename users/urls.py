from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('auth/register/', views.RegisterView.as_view(), name='user-create'),
    path('auth/login/', TokenObtainPairView.as_view(), name='user-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='user-token-refresh'),
    path('user/profile/', views.UserProfileView.as_view(), name='user-profile'),
]
