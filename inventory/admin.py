from django.contrib import admin

from .models import (
    Brand,
    BranchStock,
    Category,
    Product,
    ProductVariant,
    StockMovement,
    Unit,
    WarehouseStock,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "brand", "unit", "is_active")
    list_filter = ("category", "brand", "is_active")
    search_fields = ("name", "sku", "barcode")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "name", "sku", "size", "color", "is_active")
    search_fields = ("product__name", "name", "sku", "barcode")


@admin.register(WarehouseStock)
class WarehouseStockAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "variant", "quantity")
    search_fields = ("branch__name", "product__name", "variant__name")


@admin.register(BranchStock)
class BranchStockAdmin(admin.ModelAdmin):
    list_display = ("branch", "product", "variant", "quantity")
    search_fields = ("branch__name", "product__name", "variant__name")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_type",
        "product",
        "variant",
        "quantity",
        "source_branch",
        "dest_branch",
        "reference",
        "created_at",
        "created_by",
    )
    list_filter = ("movement_type", "source_branch", "dest_branch", "created_at")
    search_fields = ("product__name", "variant__name", "reference")


