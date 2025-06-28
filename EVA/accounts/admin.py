# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("user_type", "name", "phone_number")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("user_type", "name", "phone_number")}),
    )

    list_display = ("username", "email", "name", "phone_number", "user_type", "is_staff")

admin.site.register(CustomUser, CustomUserAdmin)
