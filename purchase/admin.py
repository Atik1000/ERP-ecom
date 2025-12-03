from django.contrib import admin

from .models import PurchaseItem, PurchaseOrder, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "email", "phone")


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "supplier", "branch", "status", "order_date")
    list_filter = ("status", "branch", "supplier")
    search_fields = ("reference", "supplier__name")
    inlines = [PurchaseItemInline]


