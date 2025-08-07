from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
import shortuuid

# ============================
# Custom User Manager
# ============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        
        full_name = extra_fields.get("full_name")
        if not full_name:
            raise ValueError(_("The Full Name field must be set"))
        
        terms_agreed = extra_fields.get("terms_agreed")
        if not terms_agreed:
            raise ValueError(_("You must agree to the Terms of Service."))

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("role") != UserRole.ADMIN:
            raise ValueError("Superuser must have role='admin'.")
        return self.create_user(email, password, **extra_fields)


# ============================
# User Roles
# ============================
class UserRole(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    FILMMAKER = 'filmmaker', _('Filmmaker')
    VIEWER = 'viewer', _('Viewer')


def generate_short_uuid():
    return shortuuid.uuid()[:12]  # shorter but still unique enough


# ============================
# Custom User Model
# ============================
class User(AbstractBaseUser, PermissionsMixin):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False ,max_length=12)
    id = models.CharField(primary_key=True, max_length=12, default=generate_short_uuid, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.VIEWER)
    otp = models.CharField(max_length=6, blank=True)
    otp_expired = models.DateTimeField(null=True, blank=True)
    reset_secret_key = models.UUIDField(blank=True, null=True)
    is_affiliate = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    terms_agreed = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email


# ============================
# Profile Model
# ============================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    language = models.CharField(max_length=50, blank=True, null=True)

    # Filmmaker specific fields
    company_name = models.CharField(max_length=150, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.email}"