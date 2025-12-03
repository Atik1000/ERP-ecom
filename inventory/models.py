from __future__ import annotations

from django.db import models
from django.db.models import Sum

from accounts.models import Branch


class Category(models.Model):
    name = models.CharField(max_length=150)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return self.name


class Unit(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)

    def __str__(self) -> str:
        return self.short_name


class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    has_variants = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

    def total_stock_quantity(self) -> float:
        """
        Helper to get total stock across all branches/warehouses for this product.
        For now this ignores variants for simplicity; later we can expand.
        """
        warehouse_total = (
            self.warehousestock_set.aggregate(total=Sum("quantity"))["total"] or 0
        )
        branch_total = (
            self.branchstock_set.aggregate(total=Sum("quantity"))["total"] or 0
        )
        return float(warehouse_total + branch_total)


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(
        max_length=150,
        help_text="e.g. Color/Size (Red / XL). Optional if product has no variants.",
    )
    size = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"


class WarehouseStock(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        limit_choices_to={"is_warehouse": True},
        related_name="warehouse_stocks",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ("branch", "product", "variant")

    def __str__(self) -> str:
        return f"{self.branch} - {self.product} ({self.variant or 'No variant'})"


class BranchStock(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        limit_choices_to={"is_warehouse": False},
        related_name="branch_stocks",
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ("branch", "product", "variant")

    def __str__(self) -> str:
        return f"{self.branch} - {self.product} ({self.variant or 'No variant'})"


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        PURCHASE_IN = "purchase_in", "Purchase (IN)"
        POS_SALE_OUT = "pos_sale_out", "POS Sale (OUT)"
        ONLINE_ORDER_OUT = "online_order_out", "Online Order (OUT)"
        TRANSFER_IN = "transfer_in", "Transfer (IN)"
        TRANSFER_OUT = "transfer_out", "Transfer (OUT)"
        RETURN_IN = "return_in", "Return (IN)"
        DAMAGE_OUT = "damage_out", "Damage (OUT)"
        ADJUSTMENT_IN = "adjustment_in", "Manual Adjustment (IN)"
        ADJUSTMENT_OUT = "adjustment_out", "Manual Adjustment (OUT)"

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    movement_type = models.CharField(max_length=50, choices=MovementType.choices)
    # Source/destination locations
    source_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_source",
    )
    dest_branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_dest",
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External reference number (invoice, order, transfer, etc.)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements_created",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} - {self.product} ({self.quantity})"


