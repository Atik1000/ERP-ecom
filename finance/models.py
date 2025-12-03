from __future__ import annotations

from django.db import models

from accounts.models import Branch, User


class CashRegister(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="cash_registers")
    date = models.DateField()
    opened_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="cash_registers_opened"
    )
    closed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cash_registers_closed",
    )
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("branch", "date")

    def __str__(self) -> str:
        return f"{self.branch} - {self.date}"


class CashEntry(models.Model):
    class Type(models.TextChoices):
        OPENING = "opening", "Opening"
        SALE = "sale", "Sale"
        PURCHASE_PAYMENT = "purchase_payment", "Purchase Payment"
        CUSTOMER_PAYMENT = "customer_payment", "Customer Payment"
        EXPENSE = "expense", "Expense"
        ADJUSTMENT = "adjustment", "Adjustment"

    register = models.ForeignKey(CashRegister, on_delete=models.CASCADE, related_name="entries")
    entry_type = models.CharField(max_length=30, choices=Type.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_inflow = models.BooleanField(
        default=True, help_text="True = money in, False = money out."
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional reference (invoice no, order id, etc.)",
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        direction = "IN" if self.is_inflow else "OUT"
        return f"{self.entry_type} {direction} {self.amount}"


class Expense(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="expenses")
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)
    paid_at = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="expenses_created"
    )

    def __str__(self) -> str:
        return f"{self.category} - {self.amount}"


