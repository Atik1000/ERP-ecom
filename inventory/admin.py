from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Brand,
    BranchStock,
    Category,
    Product,
    ProductVariant,
    StockMovement,
    StockAlert,
    StockTransfer,
    StockTransferItem,
    Unit,
    WarehouseStock,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    list_per_page = 50


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")
    search_fields = ("name", "short_name")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ("name", "sku", "size", "color", "barcode", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "brand", "selling_price", "reorder_level", "is_active", "created_at")
    list_filter = ("category", "brand", "is_active", "created_at")
    search_fields = ("name", "sku", "barcode", "description")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductVariantInline]
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "sku", "category", "brand", "unit", "description")
        }),
        ("Pricing", {
            "fields": ("cost_price", "selling_price")
        }),
        ("Stock Management", {
            "fields": ("reorder_level", "expiry_alert_days", "has_variants")
        }),
        ("Identification", {
            "fields": ("barcode", "qr_code", "image")
        }),
        ("Additional Details", {
            "fields": ("weight", "dimensions"),
            "classes": ("collapse",)
        }),
        ("Status", {
            "fields": ("is_active", "created_at", "updated_at")
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "sku", "size", "color", "is_active")
    list_filter = ("is_active",)
    search_fields = ("product__name", "name", "sku", "barcode")


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "variant", "quantity", "batch_number", "expiry_date", "last_updated")
    list_filter = ("branch", "expiry_date", "last_updated")
    search_fields = ("branch__name", "product__name", "variant__name", "batch_number")
    readonly_fields = ("last_updated",)
    date_hierarchy = "expiry_date"


@admin.register(BranchStock)
class BranchStockAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "variant", "quantity", "batch_number", "expiry_date", "last_updated")
    list_filter = ("branch", "expiry_date", "last_updated")
    search_fields = ("branch__name", "product__name", "variant__name", "batch_number")
    readonly_fields = ("last_updated",)
    date_hierarchy = "expiry_date"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "movement_type",
        "product",
        "quantity",
        "source_branch",
        "dest_branch",
        "reference",
        "created_by",
    )
    list_filter = ("movement_type", "source_branch", "dest_branch", "created_at")
    search_fields = ("product__name", "variant__name", "reference", "notes")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    
    def has_add_permission(self, request):
        # Stock movements should only be created through services
        return False
    
    def has_change_permission(self, request, obj=None):
        # Stock movements should not be edited
        return False


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = ("product", "branch", "alert_type", "current_quantity", "expiry_date", "is_resolved", "created_at")
    list_filter = ("alert_type", "is_resolved", "branch", "created_at")
    search_fields = ("product__name", "branch__name")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    
    actions = ["mark_resolved"]
    
    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
    mark_resolved.short_description = "Mark selected alerts as resolved"


class StockTransferItemInline(admin.TabularInline):
    model = StockTransferItem
    extra = 0
    fields = ("product", "variant", "requested_quantity", "approved_quantity", "received_quantity", "batch_number", "expiry_date")


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ("transfer_number", "source_branch", "destination_branch", "status", "transfer_date", "created_at")
    list_filter = ("status", "source_branch", "destination_branch", "transfer_date", "created_at")
    search_fields = ("transfer_number", "notes")
    readonly_fields = ("transfer_number", "created_at", "updated_at", "approved_at", "received_at")
    inlines = [StockTransferItemInline]
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Transfer Details", {
            "fields": ("transfer_number", "source_branch", "destination_branch", "status")
        }),
        ("Dates", {
            "fields": ("transfer_date", "expected_delivery", "actual_delivery")
        }),
        ("Workflow", {
            "fields": ("requested_by", "approved_by", "received_by", "approved_at", "received_at")
        }),
        ("Additional Information", {
            "fields": ("notes", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


