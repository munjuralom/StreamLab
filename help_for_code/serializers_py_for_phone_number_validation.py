import phonenumbers
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """For returning and updating user details."""
    
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "avatar", "phone_country_code",
            "phone_number", "role", "is_affiliate", "date_joined", "terms_agreed"
        ]
        read_only_fields = ["id", "email", "date_joined"]

    def validate(self, attrs):
        phone_code = attrs.get("phone_country_code", getattr(self.instance, "phone_country_code", None))
        phone_number = attrs.get("phone_number", getattr(self.instance, "phone_number", None))

        if phone_code and phone_number:
            try:
                # Ensure code starts with +
                if not phone_code.startswith("+"):
                    phone_code = f"+{phone_code}"

                parsed_number = phonenumbers.parse(f"{phone_code}{phone_number}")
                
                if not phonenumbers.is_possible_number(parsed_number):
                    raise serializers.ValidationError({"phone_number": "Phone number is not possible for that country."})
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError({"phone_number": "Invalid phone number for that country."})

            except phonenumbers.NumberParseException:
                raise serializers.ValidationError({"phone_number": "Invalid phone number format."})

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """For user registration with validation."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "email", "full_name", "password",
            "phone_country_code", "phone_number",
            "role", "terms_agreed"
        ]

    def validate(self, attrs):
        phone_code = attrs.get("phone_country_code")
        phone_number = attrs.get("phone_number")

        if phone_code and phone_number:
            try:
                if not phone_code.startswith("+"):
                    phone_code = f"+{phone_code}"

                parsed_number = phonenumbers.parse(f"{phone_code}{phone_number}")
                
                if not phonenumbers.is_possible_number(parsed_number):
                    raise serializers.ValidationError({"phone_number": "Phone number is not possible for that country."})
                if not phonenumbers.is_valid_number(parsed_number):
                    raise serializers.ValidationError({"phone_number": "Invalid phone number for that country."})

            except phonenumbers.NumberParseException:
                raise serializers.ValidationError({"phone_number": "Invalid phone number format."})

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user
