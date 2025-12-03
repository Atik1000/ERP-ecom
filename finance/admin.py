from django.contrib import admin
from .models import ExpenseCategory, Expense, BankAccount


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    readonly_fields = ["created_at"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = [
        "reference",
        "branch",
        "category",
        "amount",
        "payment_method",
        "expense_date",
        "is_approved"
    ]
    list_filter = ["is_approved", "payment_method", "branch", "expense_date"]
    search_fields = ["reference", "category__name", "description"]
    readonly_fields = ["created_at", "created_by"]
    date_hierarchy = "expense_date"
    actions = ["approve_expenses", "reject_expenses"]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def approve_expenses(self, request, queryset):
        updated = queryset.filter(is_approved=False).update(is_approved=True)
        self.message_user(request, f"{updated} expenses approved.")
    approve_expenses.short_description = "Approve selected expenses"
    
    def reject_expenses(self, request, queryset):
        updated = queryset.filter(is_approved=True).update(is_approved=False)
        self.message_user(request, f"{updated} expenses rejected.")
    reject_expenses.short_description = "Reject selected expenses"


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        "account_number",
        "bank_name",
        "branch",
        "is_active"
    ]
    list_filter = ["is_active", "bank_name", "branch"]
    search_fields = ["account_number", "bank_name"]
    readonly_fields = ["created_at"]
