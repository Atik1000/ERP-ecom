from __future__ import annotations

from decimal import Decimal
from django.db import models

from accounts.models import Branch, User


class ExpenseCategory(models.Model):
    """Categories for expenses"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    """Track business expenses"""
    
    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CARD = "card", "Card"
        CHEQUE = "cheque", "Cheque"
    
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="expenses")
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses"
    )
    reference = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH
    )
    description = models.TextField(blank=True)
    receipt_image = models.ImageField(upload_to="expenses/", blank=True, null=True)
    expense_date = models.DateField()
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses"
    )
    is_approved = models.BooleanField(default=False)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name="expenses_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-expense_date", "-created_at"]
        indexes = [
            models.Index(fields=["-expense_date"]),
            models.Index(fields=["branch", "-expense_date"]),
            models.Index(fields=["category", "-expense_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.category.name} - {self.amount} - {self.expense_date}"


class Transaction(models.Model):
    """Generic financial transactions"""
    
    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"
        TRANSFER = "transfer", "Transfer"
    
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    transaction_date = models.DateField()
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="transactions_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["-transaction_date"]),
            models.Index(fields=["branch", "-transaction_date"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.transaction_date}"


class BankAccount(models.Model):
    """Company bank accounts"""
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="bank_accounts"
    )
    bank_name = models.CharField(max_length=150)
    account_name = models.CharField(max_length=200)
    account_number = models.CharField(max_length=50)
    account_type = models.CharField(
        max_length=50,
        choices=[
            ("checking", "Checking"),
            ("savings", "Savings"),
            ("current", "Current"),
        ]
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["bank_name", "account_name"]
    
    def __str__(self) -> str:
        return f"{self.bank_name} - {self.account_number}"


class DailyCashReport(models.Model):
    """Daily cash summary for branches"""
    
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="daily_cash_reports")
    report_date = models.DateField()
    
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_receipts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    expected_closing = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    difference = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    notes = models.TextField(blank=True)
    
    prepared_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="cash_reports_prepared"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cash_reports_approved"
    )
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("branch", "report_date")
        ordering = ["-report_date"]
        indexes = [
            models.Index(fields=["branch", "-report_date"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.branch.name} - {self.report_date}"


