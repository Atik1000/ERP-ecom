from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.utils import timezone

from accounts.models import User
from inventory.models import Product


class CustomerGroup(models.Model):
    """Customer segments for targeted marketing and pricing"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0, 
        help_text="Default discount % for this group"
    )
    points_multiplier = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="Loyalty points earning multiplier"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CustomerGroupMembership(models.Model):
    """Assign customers to groups"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_groups")
    group = models.ForeignKey(CustomerGroup, on_delete=models.CASCADE, related_name="members")
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("user", "group")
        ordering = ["-joined_at"]
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.group.name}"


class LoyaltyPoints(models.Model):
    """Track customer loyalty points"""
    
    class TransactionType(models.TextChoices):
        EARNED = "earned", "Earned"
        REDEEMED = "redeemed", "Redeemed"
        EXPIRED = "expired", "Expired"
        ADJUSTED = "adjusted", "Adjusted"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loyalty_points")
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    points = models.IntegerField()
    balance_after = models.IntegerField(default=0)
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Loyalty Points"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.points} pts - {self.get_transaction_type_display()}"


class Coupon(models.Model):
    """Discount coupons for customers"""
    
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Percentage"
        FIXED = "fixed", "Fixed Amount"
        FREE_SHIPPING = "free_shipping", "Free Shipping"
    
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    
    # Usage limits
    max_uses = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Total number of times this coupon can be used"
    )
    used_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Max uses per customer"
    )
    
    # Restrictions
    min_purchase_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Minimum cart value required"
    )
    applicable_products = models.ManyToManyField(
        Product,
        blank=True,
        related_name="coupons",
        help_text="Leave empty for all products"
    )
    customer_groups = models.ManyToManyField(
        CustomerGroup,
        blank=True,
        related_name="coupons",
        help_text="Leave empty for all customers"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self) -> str:
        return self.code
    
    def is_valid(self) -> bool:
        """Check if coupon is currently valid"""
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_to:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True
    
    def can_be_used_by(self, user: User) -> bool:
        """Check if user can use this coupon"""
        if not self.is_valid():
            return False
        if self.per_user_limit:
            usage_count = self.usages.filter(user=user).count()
            if usage_count >= self.per_user_limit:
                return False
        return True


class CouponUsage(models.Model):
    """Track coupon usage"""
    
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coupon_usages")
    order_reference = models.CharField(
        max_length=100,
        help_text="Order/Invoice number"
    )
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-used_at"]
        indexes = [
            models.Index(fields=["user", "-used_at"]),
            models.Index(fields=["coupon", "-used_at"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.coupon.code} used by {self.user.username}"


class Feedback(models.Model):
    """Customer feedback for orders"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="feedbacks"
    )
    order_reference = models.CharField(max_length=100)
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)],
        default=5
    )
    comment = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_reference"]),
            models.Index(fields=["is_published", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"Feedback {self.rating} stars for {self.order_reference}"


class Newsletter(models.Model):
    """Newsletter subscriptions"""
    
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ["-subscribed_at"]
    
    def __str__(self) -> str:
        return self.email


