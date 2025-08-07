from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'role',
            'is_affiliate', 'is_active', 'is_staff','date_joined',
        ]
        read_only_fields = ['id', 'is_active', 'is_staff']
