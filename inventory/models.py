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
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    barcode = models.CharField(max_length=100, blank=True, null=True, unique=True)
    qr_code = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    has_variants = models.BooleanField(default=False)
    
    # Stock management fields
    reorder_level = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        help_text="Alert when stock falls below this level"
    )
    expiry_alert_days = models.IntegerField(
        default=30,
        help_text="Alert this many days before expiry"
    )
    
    # Product details
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("branch", "product", "variant", "batch_number")
        indexes = [
            models.Index(fields=["product", "branch"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.branch} - {self.product} ({self.variant or 'No variant'})"
    
    def is_low_stock(self) -> bool:
        """Check if stock is below reorder level"""
        return self.quantity <= self.product.reorder_level
    
    def is_expiring_soon(self) -> bool:
        """Check if product is expiring soon"""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        from datetime import timedelta
        alert_date = timezone.now().date() + timedelta(days=self.product.expiry_alert_days)
        return self.expiry_date <= alert_date


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
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("branch", "product", "variant", "batch_number")
        indexes = [
            models.Index(fields=["product", "branch"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self) -> str:
        return f"{self.branch} - {self.product} ({self.variant or 'No variant'})"
    
    def is_low_stock(self) -> bool:
        """Check if stock is below reorder level"""
        return self.quantity <= self.product.reorder_level
    
    def is_expiring_soon(self) -> bool:
        """Check if product is expiring soon"""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        from datetime import timedelta
        alert_date = timezone.now().date() + timedelta(days=self.product.expiry_alert_days)
        return self.expiry_date <= alert_date


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
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    cost_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="For FIFO cost tracking"
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
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["product", "-created_at"]),
            models.Index(fields=["movement_type", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_movement_type_display()} - {self.product} ({self.quantity})"


class StockAlert(models.Model):
    """Track low stock and expiry alerts"""
    
    class AlertType(models.TextChoices):
        LOW_STOCK = "low_stock", "Low Stock"
        EXPIRING_SOON = "expiring_soon", "Expiring Soon"
        EXPIRED = "expired", "Expired"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    current_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_resolved", "-created_at"]),
            models.Index(fields=["product", "branch"]),
        ]
    
    def __str__(self) -> str:
        return f"{self.get_alert_type_display()} - {self.product} @ {self.branch}"


class StockTransfer(models.Model):
    """Transfer stock between warehouses and branches"""
    
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        IN_TRANSIT = "in_transit", "In Transit"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
    
    transfer_number = models.CharField(max_length=100, unique=True)
    source_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transfers_out"
    )
    destination_branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="transfers_in"
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transfer_date = models.DateField()
    expected_delivery = models.DateField(null=True, blank=True)
    actual_delivery = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    # Workflow tracking
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="transfers_requested"
    )
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_approved"
    )
    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_received"
    )
    
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["source_branch", "-created_at"]),
            models.Index(fields=["destination_branch", "-created_at"]),
            models.Index(fields=["transfer_number"]),
        ]
    
    def __str__(self) -> str:
        return f"Transfer {self.transfer_number}: {self.source_branch} → {self.destination_branch}"
    
    def can_be_approved(self) -> bool:
        """Check if transfer can be approved"""
        return self.status == self.Status.PENDING
    
    def can_be_received(self) -> bool:
        """Check if transfer can be received"""
        return self.status in [self.Status.APPROVED, self.Status.IN_TRANSIT]


class StockTransferItem(models.Model):
    """Items in a stock transfer"""
    
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    requested_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    approved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Quantity approved for transfer"
    )
    received_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Quantity actually received"
    )
    
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ["id"]
    
    def __str__(self) -> str:
        return f"{self.product.name} x {self.requested_quantity}"
    
    def is_fully_received(self) -> bool:
        """Check if item is fully received"""
        return self.received_quantity >= self.approved_quantity


