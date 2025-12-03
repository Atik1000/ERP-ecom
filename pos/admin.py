from django.contrib import admin
from .models import CashRegister, PosSession, PosSale, PosSaleItem, PosPayment


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "branch", "is_active", "created_at"]
    list_filter = ["is_active", "branch"]
    search_fields = ["code", "name", "branch__name"]
    readonly_fields = ["created_at"]


@admin.register(PosSession)
class PosSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "branch",
        "cash_register",
        "cashier",
        "opened_at",
        "closed_at",
        "is_closed"
    ]
    list_filter = ["is_closed", "branch", "opened_at"]
    search_fields = ["cashier__username", "cash_register__name"]
    readonly_fields = ["opened_at", "closed_at", "difference"]


@admin.register(PosSale)
class PosSaleAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "branch",
        "cashier",
        "customer"
    ]
    list_filter = ["branch"]
    search_fields = ["invoice_number", "customer__username", "cashier__username"]
    readonly_fields = ["invoice_number"]


@admin.register(PosSaleItem)
class PosSaleItemAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "product",
        "variant",
        "quantity",
        "unit_price"
    ]
    list_filter = ["sale__branch"]
    search_fields = ["product__name", "sale__invoice_number"]


@admin.register(PosPayment)
class PosPaymentAdmin(admin.ModelAdmin):
    list_display = [
        "sale",
        "amount",
        "reference"
    ]
    search_fields = ["sale__invoice_number", "reference"]
