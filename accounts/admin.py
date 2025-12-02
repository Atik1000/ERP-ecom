from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Branch, BranchUserAssignment, User


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_warehouse", "is_active")
    list_filter = ("is_warehouse", "is_active")
    search_fields = ("name", "code")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "SmartERP Role & Branch",
            {
                "fields": (
                    "role",
                    "default_branch",
                )
            },
        ),
    )
    list_display = ("username", "email", "role", "default_branch", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "groups")


@admin.register(BranchUserAssignment)
class BranchUserAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "is_primary")
    list_filter = ("is_primary",)
    search_fields = ("user__username", "branch__name", "branch__code")


