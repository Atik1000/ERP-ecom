from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.utils import timezone

from accounts.models import Branch, User
from inventory.models import Product, ProductVariant


class CashRegister(models.Model):
    """Physical cash register at a branch"""
    
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="cash_registers")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["branch", "name"]
    
    def __str__(self) -> str:
        return f"{self.name} - {self.branch}"


class PosSession(models.Model):
    """
    Cash register session for a branch and cashier.
    """

    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="pos_sessions")
    cash_register = models.ForeignKey(
        CashRegister, 
        on_delete=models.PROTECT, 
        related_name="sessions",
        null=True,
        blank=True
    )
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name="pos_sessions")
    opened_at = models.DateTimeField(default=timezone.now)
    closed_at = models.DateTimeField(null=True, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expected_closing = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-opened_at"]
        indexes = [
            models.Index(fields=["-opened_at"]),
            models.Index(fields=["branch", "-opened_at"]),
            models.Index(fields=["cashier", "-opened_at"]),
        ]

    def __str__(self) -> str:
        return f"POS Session {self.id} - {self.branch} - {self.cashier}"
    
    def calculate_expected_closing(self):
        """Calculate expected closing balance"""
        total_sales = sum(
            sale.grand_total for sale in self.sales.filter(status="completed")
        )
        self.expected_closing = self.opening_balance + total_sales
        return self.expected_closing
    
    def calculate_difference(self):
        """Calculate cash difference"""
        if self.closing_balance is not None:
            self.difference = self.closing_balance - self.expected_closing
        return self.difference


class PosSale(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
    
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        MOBILE_BANKING = "mobile_banking", "Mobile Banking"
        MIXED = "mixed", "Mixed Payment"

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
    invoice_number = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Payment fields
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    change_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    is_synced = models.BooleanField(
        default=True,
        help_text="False if created offline and needs syncing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["branch", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["invoice_number"]),
        ]

    def __str__(self) -> str:
        return f"POS Sale {self.invoice_number} - {self.branch}"
    
    def calculate_totals(self):
        """Recalculate all financial totals"""
        self.subtotal = sum(item.get_line_total() for item in self.items.all())
        
        if self.discount_percent > 0:
            self.discount_amount = (self.subtotal * self.discount_percent) / 100
        
        amount_after_discount = self.subtotal - self.discount_amount
        
        if self.vat_percent > 0:
            self.vat_amount = (amount_after_discount * self.vat_percent) / 100
        
        self.grand_total = amount_after_discount + self.vat_amount
        self.change_amount = self.amount_paid - self.grand_total if self.amount_paid > self.grand_total else 0
        
        self.save(update_fields=['subtotal', 'discount_amount', 'vat_amount', 'grand_total', 'change_amount'])


class PosSaleItem(models.Model):
    sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
    
    def get_line_total(self) -> Decimal:
        """Calculate line total after discount"""
        line_total = Decimal(self.unit_price) * Decimal(self.quantity)
        return line_total - Decimal(self.discount_amount)


class PosPayment(models.Model):
    """Track multiple payment methods for a single sale"""
    
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        MOBILE = "mobile", "Mobile Banking"

    sale = models.ForeignKey(PosSale, on_delete=models.CASCADE, related_name="split_payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.get_method_display()} {self.amount}"


