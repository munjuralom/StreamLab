# models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import phonenumbers
import uuid


class UserRole(models.TextChoices):
    FILMMAKER = "filmmaker", "Filmmaker"
    VIEWER = "viewer", "Viewer"


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices)
    terms_agreed = models.BooleanField(default=False)

    # Phone number fields
    country_code = models.CharField(max_length=5, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expired = models.DateTimeField(blank=True, null=True)
    reset_secret_key = models.UUIDField(blank=True, null=True)

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]

    def __str__(self):
        return self.email

    def clean(self):
        """
        Validate phone number globally using phonenumbers library.
        """
        if self.country_code and self.phone_number:
            try:
                parsed_number = phonenumbers.parse(f"+{self.country_code}{self.phone_number}")
                if not phonenumbers.is_valid_number(parsed_number):
                    from django.core.exceptions import ValidationError
                    raise ValidationError({"phone_number": "Invalid phone number for given country code."})
            except phonenumbers.NumberParseException:
                from django.core.exceptions import ValidationError
                raise ValidationError({"phone_number": "Invalid phone number format."})
