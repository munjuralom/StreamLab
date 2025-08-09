from rest_framework import serializers
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
from .accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    refer_by_code = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "avatar",
            "phone_country_code", "phone_number",
            "role", "is_affiliate", "date_joined",
            "refer_by_code",  # input referral code string
            "password",
        ]
        read_only_fields = ["id", "email", "role", "is_affiliate", "date_joined"]

    def validate(self, data):
        country_code = data.get("phone_country_code") or getattr(self.instance, "phone_country_code", None)
        phone_number = data.get("phone_number") or getattr(self.instance, "phone_number", None)

        if country_code and phone_number:
            cc = country_code.lstrip("+").strip()
            if not cc.isdigit():
                raise serializers.ValidationError({"phone_country_code": "Country code must be numeric."})

            valid_country_codes = set(_COUNTRY_CODE_TO_REGION_CODE.keys())
            cc_int = int(cc)
            if cc_int not in valid_country_codes:
                raise serializers.ValidationError({"phone_country_code": "Invalid country calling code."})

            pn = phone_number.strip()
            e164_number = f"+{cc}{pn}"

            try:
                parsed = phonenumbers.parse(e164_number, None)
            except NumberParseException:
                raise serializers.ValidationError({"phone_number": "Invalid phone number format."})

            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError({"phone_number": "Invalid phone number for the given country code."})

            # Normalize for storage
            data["phone_country_code"] = str(parsed.country_code)
            normalized_national = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
            normalized_national = normalized_national.replace(" ", "").replace("-", "")
            data["phone_number"] = normalized_national

        return data

    def validate_refer_by_code(self, value):
        if not value:
            return None
        try:
            user = User.objects.get(referral_code=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid referral code.")
        return user

    def create(self, validated_data):
        refer_by_user = validated_data.pop("refer_by_code", None)
        password = validated_data.pop("password", None)

        if refer_by_user:
            validated_data["refer_by"] = refer_by_user

        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        refer_by_user = validated_data.pop("refer_by_code", None)
        password = validated_data.pop("password", None)

        if refer_by_user:
            instance.refer_by = refer_by_user

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
