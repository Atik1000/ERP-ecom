from __future__ import annotations

from django.db import models

from accounts.models import Branch, User
from inventory.models import Product, ProductVariant


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipping_addresses")
    full_name = models.CharField(max_length=255)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="Bangladesh")
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.full_name} - {self.city}"


class WebOrder(models.Model):
    class Status(models.TextChoices):
        CART = "cart", "Cart"
        PENDING = "pending", "Pending Payment"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name="web_orders")
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="web_orders",
        help_text="Fulfilment branch/warehouse",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CART)
    shipping_address = models.ForeignKey(
        ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reserved_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Optional cart stock reservation expiry.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Web Order #{self.id} - {self.customer}"


class WebOrderItem(models.Model):
    order = models.ForeignKey(WebOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount_amount


