from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'id', 'full_name', 'role', 'is_affiliate', 'is_active', 'is_staff', 'terms_agreed', 'date_joined')
    list_filter = ('role', 'is_affiliate', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name',)}),
        ('Roles & Permissions', {'fields': ('role', 'is_affiliate', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('OTP Info', {'fields': ('otp', 'otp_expired', 'reset_secret_key')}),
        ('Terms & Agreed', {'fields': ('terms_agreed',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'password1', 'password2', 'is_affiliate', 'is_active', 'is_staff')}
        ),
    )

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'country')
    search_fields = ('user__email', 'phone_number', 'country')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
