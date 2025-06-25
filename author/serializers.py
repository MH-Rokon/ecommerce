from rest_framework import serializers
from .models import User  
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Serializer for retrieving user info
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']  # adjust fields as needed

class RegistrationSerializer(serializers.ModelSerializer):
    # Serializer for user registration with password confirmation
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.is_active = False  # deactivate until email confirmation
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    # Serializer for user login credentials
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

class PasswordResetRequestSerializer(serializers.Serializer):
    # Serializer to request password reset via email
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    # Serializer to confirm password reset with new password
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
