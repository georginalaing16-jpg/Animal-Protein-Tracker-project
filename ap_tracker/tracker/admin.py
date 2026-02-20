from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Show weight_kg in the user list page
    list_display = BaseUserAdmin.list_display + ("weight_kg",)

    # Add weight_kg to the user edit page
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Health Info", {"fields": ("weight_kg",)}),
    )

    # Add weight_kg to the "Add user" page too
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Health Info", {"fields": ("weight_kg",)}),
    )