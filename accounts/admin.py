from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Branch, BranchUserAssignment, User, ActivityLog


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_warehouse", "phone", "is_active", "created_at")
    list_filter = ("is_warehouse", "is_active", "created_at")
    search_fields = ("name", "code", "phone", "email")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "code", "is_warehouse", "is_active")
        }),
        ("Contact Details", {
            "fields": ("phone", "email", "address")
        }),
        ("Hierarchy", {
            "fields": ("parent_branch",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "SmartERP Profile",
            {
                "fields": (
                    "role",
                    "default_branch",
                    "phone",
                    "address",
                    "profile_image",
                    "is_active_staff",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            }
        ),
    )
    list_display = ("username", "email", "role", "default_branch", "is_active_staff", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser", "is_active", "is_active_staff", "groups")
    search_fields = ("username", "email", "first_name", "last_name", "phone")
    readonly_fields = ("created_at", "updated_at")


@admin.register(BranchUserAssignment)
class BranchUserAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "is_primary")
    list_filter = ("is_primary", "branch")
    search_fields = ("user__username", "branch__name", "branch__code")
    autocomplete_fields = ["user", "branch"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action_type", "model_name", "created_at")
    list_filter = ("action_type", "created_at")
    search_fields = ("user__username", "model_name", "description")
    readonly_fields = ("user", "action_type", "model_name", "object_id", "description", 
                      "ip_address", "user_agent", "created_at")
    date_hierarchy = "created_at"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


