from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    is_warehouse = models.BooleanField(default=False)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    parent_branch = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="child_branches",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Branch / Warehouse"
        verbose_name_plural = "Branches & Warehouses"

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        WAREHOUSE_MANAGER = "warehouse_manager", "Warehouse Manager"
        BRANCH_MANAGER = "branch_manager", "Branch Manager"
        CASHIER = "cashier", "Cashier"
        CUSTOMER = "customer", "Customer"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="Controls access and sidebar visibility.",
    )
    default_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(
        upload_to="profiles/", blank=True, null=True
    )
    is_active_staff = models.BooleanField(
        default=True,
        help_text="Designates whether this user can access the system.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"


class BranchUserAssignment(models.Model):
    """
    Optional: allow a user to be assigned to multiple branches.
    The `default_branch` on User is the primary one, but this records all.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="branch_links")
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="user_links"
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "branch")
        verbose_name = "Branch User Assignment"
        verbose_name_plural = "Branch User Assignments"

    def __str__(self) -> str:
        return f"{self.user} @ {self.branch}"


class ActivityLog(models.Model):
    """Track important user actions for audit purposes"""
    
    class ActionType(models.TextChoices):
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        APPROVE = "approve", "Approve"
        REJECT = "reject", "Reject"
        
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="activity_logs"
    )
    action_type = models.CharField(max_length=20, choices=ActionType.choices)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]
        
    def __str__(self) -> str:
        return f"{self.user} - {self.get_action_type_display()} - {self.created_at}"


