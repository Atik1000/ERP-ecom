from __future__ import annotations

from django.db import models

from accounts.models import Branch, User
from inventory.models import Product, ProductVariant


class PosSession(models.Model):
    """
    Cash register session for a branch and cashier.
    """

    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="pos_sessions")
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name="pos_sessions")
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"POS Session {self.id} - {self.branch} - {self.cashier}"


class PosSale(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="pos_sales")
    session = models.ForeignKey(
        PosSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales"
    )
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name="pos_sales")
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pos_purchases",
        help_text="Optional customer (must have customer role).",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"POS Sale #{self.id} - {self.branch}"


class PosSaleItem(models.Model):
    sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def line_total(self):
        return (self.unit_price * self.quantity) - self.discount_amount


class PosPayment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        MOBILE = "mobile", "Mobile Banking"

    sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.get_method_display()} {self.amount}"


