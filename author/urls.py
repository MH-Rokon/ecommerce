from django.urls import path
from .views import (
    RegistrationAPIView, ActivateAccountAPIView,
    LoginAPIView, LogoutAPIView,
    PasswordResetRequestAPIView, PasswordResetConfirmAPIView,ProfileAPIView
)

urlpatterns = [
    path('register/', RegistrationAPIView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountAPIView.as_view(), name='activate'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password_reset'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirmAPIView.as_view(), name='password_reset_confirm'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]
