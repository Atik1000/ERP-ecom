from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.utils import timezone
from datetime import timedelta

from accounts.models import Branch, User
from inventory.models import Product, ProductVariant


class ShippingAddress(models.Model):
    """Customer shipping addresses"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping_addresses")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Bangladesh")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Shipping Addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.city}"


class Cart(models.Model):
    """Shopping cart for customers"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="cart",
        limit_choices_to={"role": "customer"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-updated_at"]
    
    def __str__(self) -> str:
        return f"Cart - {self.user.username}"
    
    def get_total_items(self) -> int:
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    def get_subtotal(self) -> Decimal:
        """Calculate cart subtotal"""
        return sum(item.get_total() for item in self.items.all())
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in shopping cart"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    reserved_until = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Stock reserved until this time (15 minutes)"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("cart", "product", "variant")
        ordering = ["-added_at"]
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self) -> Decimal:
        """Calculate item total"""
        return Decimal(self.product.selling_price) * Decimal(self.quantity)
    
    def reserve_stock(self):
        """Reserve stock for 15 minutes"""
        self.reserved_until = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['reserved_until'])
    
    def is_reservation_valid(self) -> bool:
        """Check if stock reservation is still valid"""
        if not self.reserved_until:
            return False
        return timezone.now() < self.reserved_until


class OnlineOrder(models.Model):
    """Online orders from e-commerce site"""
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending Payment"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"
    
    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        CARD = "card", "Credit/Debit Card"
        MOBILE_BANKING = "mobile_banking", "Mobile Banking"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    
    customer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name="online_orders",
        limit_choices_to={"role": "customer"}
    )
    order_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Shipping information
    shipping_address = models.ForeignKey(
        ShippingAddress, 
        on_delete=models.PROTECT,
        related_name="orders"
    )
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment info
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("unpaid", "Unpaid"),
            ("paid", "Paid"),
            ("refunded", "Refunded"),
        ],
        default="unpaid"
    )
    transaction_id = models.CharField(max_length=200, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Fulfillment branch
    fulfillment_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="online_orders_fulfilled"
    )
    
    notes = models.TextField(blank=True)
    customer_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["order_number"]),
        ]
    
    def __str__(self) -> str:
        return f"Order {self.order_number} - {self.customer.username}"
    
    def calculate_totals(self):
        """Recalculate all financial totals"""
        self.subtotal = sum(item.get_total() for item in self.items.all())
        self.grand_total = self.subtotal + self.shipping_cost + self.vat_amount - self.discount_amount
        self.save(update_fields=['subtotal', 'grand_total'])
    
    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled"""
        return self.status in ["pending", "paid", "processing"]


class OrderItem(models.Model):
    """Items in an online order"""
    
    order = models.ForeignKey(OnlineOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ["id"]
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
    
    def get_total(self) -> Decimal:
        """Calculate line total"""
        return (Decimal(self.unit_price) * Decimal(self.quantity)) - Decimal(self.discount_amount)


class Wishlist(models.Model):
    """Customer wishlist"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist",
        limit_choices_to={"role": "customer"}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f"Wishlist - {self.user.username}"


class WishlistItem(models.Model):
    """Items in wishlist"""
    
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("wishlist", "product", "variant")
        ordering = ["-added_at"]
    
    def __str__(self) -> str:
        return f"{self.product.name}"


class ProductReview(models.Model):
    """Customer product reviews"""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    order = models.ForeignKey(
        OnlineOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["is_approved", "-created_at"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.product.name} - {self.rating} stars by {self.user.username}"


