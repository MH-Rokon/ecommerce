from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers 
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated


User = get_user_model()


class RegistrationAPIView(APIView):
    # API view for user registration with email activation
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        # Handle user registration and send activation email
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  
            user.save()

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = f"https://ecommerce-y7dt.onrender.com/api/activate/{uid}/{token}/"  # Fixed path

            subject = "Activate Your Account"
            message = f"Welcome! Activate your account by clicking this link:\n\n{activation_link}"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                user.delete()  
                return Response(
                    {"error": f"Failed to send confirmation email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response(
                {"detail": "Registration successful. Please check your email to activate your account."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountAPIView(APIView):
    # API view to activate user account via emailed token
    def get(self, request, uidb64, token):
        # Validate activation token and activate user
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Account activated successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Activation link is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    # API view to handle user login and JWT token generation
    serializer_class = serializers.UserLoginSerializer

    def post(self, request):
        # Authenticate user and return JWT tokens
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user:
                if not user.is_active:
                    return Response({"error": "Account not active. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)

                refresh = RefreshToken.for_user(user)

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id
                }, status=status.HTTP_200_OK)

            return Response({'error': "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileAPIView(APIView):
    # API view to retrieve authenticated user's profile data
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        # Return current user's serialized data
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutAPIView(APIView):
    # API view to handle user logout and blacklist refresh token
    def post(self, request):
        # Blacklist the refresh token on logout
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(APIView):
    # API view to request password reset email
    serializer_class = serializers.PasswordResetRequestSerializer

    def post(self, request):
        # Send password reset email if user exists
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"detail": "If this email is registered, you'll receive a password reset email."})

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"https://ecommerce-y7dt.onrender.com/api/reset-password-confirm/{uid}/{token}/"  # Fixed path

            subject = "Password Reset Request"
            message = (
                f"Hi,\n\nYou requested a password reset. Click below to reset your password:\n\n"
                f"{reset_link}\n\nIf you didn’t request this, ignore this email."
            )

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                return Response(
                    {"error": f"Failed to send reset email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({"detail": "If this email is registered, you will receive a password reset link."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPIView(APIView):
    # API view to confirm password reset using token and set new password
    serializer_class = serializers.PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        # Validate reset token and update user's password
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                uid = urlsafe_base64_decode(uidb64).decode()
                user = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError, TypeError, OverflowError):
                return Response({"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





