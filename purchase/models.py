from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.db.models import Sum, F

from accounts.models import Branch, User
from inventory.models import Product, ProductVariant


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    contact_person = models.CharField(max_length=150, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    tax_number = models.CharField(max_length=100, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
    
    def get_total_due(self) -> Decimal:
        """Calculate total due amount"""
        return self.current_balance


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ORDERED = "ordered", "Ordered"
        PARTIAL = "partial", "Partially Received"
        RECEIVED = "received", "Fully Received"
        CANCELLED = "cancelled", "Cancelled"

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="purchase_orders")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="purchase_orders")
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    order_date = models.DateField()
    expected_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    
    # Financial fields
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="purchase_orders_created")
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="purchase_orders_received")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-order_date", "-id"]
        indexes = [
            models.Index(fields=["-order_date"]),
            models.Index(fields=["supplier", "-order_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"PO {self.reference} - {self.supplier}"
    
    def get_due_amount(self) -> Decimal:
        """Calculate remaining due amount"""
        return self.total_amount - self.paid_amount
    
    def is_fully_paid(self) -> bool:
        """Check if purchase is fully paid"""
        return self.paid_amount >= self.total_amount
    
    def calculate_totals(self):
        """Recalculate all financial totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.get_total() for item in items)
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.save(update_fields=['subtotal', 'total_amount'])


class PurchaseItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.quantity} @ {self.unit_cost}"
    
    def get_total(self) -> Decimal:
        """Calculate line total"""
        return Decimal(self.quantity) * Decimal(self.unit_cost)
    
    def get_pending_quantity(self) -> Decimal:
        """Calculate remaining quantity to receive"""
        return Decimal(self.quantity) - Decimal(self.received_quantity)
    
    def is_fully_received(self) -> bool:
        """Check if item is fully received"""
        return self.received_quantity >= self.quantity


class SupplierPayment(models.Model):
    """Track payments made to suppliers"""
    
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CHEQUE = "cheque", "Cheque"
        CARD = "card", "Card"
        MOBILE_BANKING = "mobile_banking", "Mobile Banking"
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="payments")
    purchase_order = models.ForeignKey(
        PurchaseOrder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="payments"
    )
    reference = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_date = models.DateField()
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="supplier_payments_created")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-payment_date", "-id"]
        indexes = [
            models.Index(fields=["-payment_date"]),
            models.Index(fields=["supplier", "-payment_date"]),
        ]
    
    def __str__(self) -> str:
        return f"Payment {self.reference} - {self.supplier} - {self.amount}"


