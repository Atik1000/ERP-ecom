from __future__ import annotations

from decimal import Decimal
from django.db import models

from accounts.models import User, Branch
from inventory.models import Product, ProductVariant


class SalesReturn(models.Model):
    """Handle returns for both POS and online sales"""
    
    class ReturnType(models.TextChoices):
        POS_RETURN = "pos_return", "POS Return"
        ONLINE_RETURN = "online_return", "Online Return"
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
    
    return_number = models.CharField(max_length=100, unique=True)
    return_type = models.CharField(max_length=20, choices=ReturnType.choices)
    
    # Link to original sale (using CharField to avoid circular import)
    reference_number = models.CharField(
        max_length=100,
        help_text="Invoice/Order number of original sale"
    )
    
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sales_returns")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="sales_returns")
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_returns"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["return_number"]),
        ]
    
    def __str__(self) -> str:
        return f"Return {self.return_number} - {self.customer.username}"
    
    def calculate_total(self):
        """Calculate total return amount"""
        self.total_amount = sum(item.get_total() for item in self.items.all())
        self.save(update_fields=['total_amount'])


class SalesReturnItem(models.Model):
    """Items in a sales return"""
    
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        ordering = ["id"]
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self) -> Decimal:
        """Calculate line total"""
        return Decimal(self.quantity) * Decimal(self.unit_price)


class SalesTarget(models.Model):
    """Set sales targets for branches or staff"""
    
    class TargetType(models.TextChoices):
        BRANCH = "branch", "Branch Target"
        USER = "user", "User Target"
    
    target_type = models.CharField(max_length=20, choices=TargetType.choices)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="sales_targets",
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sales_targets",
        null=True,
        blank=True
    )
    
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    achieved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-period_start"]
        indexes = [
            models.Index(fields=["branch", "-period_start"]),
            models.Index(fields=["user", "-period_start"]),
        ]
    
    def __str__(self) -> str:
        if self.branch:
            return f"Target - {self.branch.name} - {self.period_start}"
        return f"Target - {self.user.username} - {self.period_start}"
    
    def get_achievement_percentage(self) -> float:
        """Calculate achievement percentage"""
        if self.target_amount == 0:
            return 0
        return (float(self.achieved_amount) / float(self.target_amount)) * 100



