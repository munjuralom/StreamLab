from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    """For returning user details (safe to expose)."""
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "avatar", "phone_country_code", "phone_number", "role", "is_affiliate", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]


# class RegisterSerializer(serializers.ModelSerializer):
#     """For user registration."""
#     password = serializers.CharField(write_only=True, min_length=6)

#     class Meta:
#         model = User
#         fields = ["email", "full_name", "password", "phone_country_code", "phone_number", "role", "terms_agreed"]

#     def create(self, validated_data):
#         password = validated_data.pop("password")
#         user = User.objects.create_user(password=password, **validated_data)
#         return user


# class LoginSerializer(serializers.Serializer):
#     """For user login."""
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = authenticate(email=data["email"], password=data["password"])
#         if not user:
#             raise serializers.ValidationError("Invalid email or password.")
#         if not user.is_active:
#             raise serializers.ValidationError("This account is inactive.")
#         data["user"] = user
#         return data
