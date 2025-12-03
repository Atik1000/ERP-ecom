from __future__ import annotations

from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import date

from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone

from accounts.models import Branch, User
from inventory.models import (
    BranchStock,
    Product,
    ProductVariant,
    StockMovement,
    WarehouseStock,
    StockAlert,
)


class InsufficientStockError(Exception):
    """Raised when there's not enough stock for an operation"""
    pass


class StockService:
    """Centralized service for all stock operations"""
    
    @staticmethod
    @transaction.atomic
    def apply_stock_movement(
        *,
        product: Product,
        variant: Optional[ProductVariant] = None,
        quantity: Decimal,
        movement_type: str,
        source_branch: Optional[Branch] = None,
        dest_branch: Optional[Branch] = None,
        reference: str = "",
        batch_number: str = "",
        expiry_date: Optional[date] = None,
        cost_price: Optional[Decimal] = None,
        notes: str = "",
        created_by: Optional[User] = None,
    ) -> StockMovement:
        """
        Central service for all stock changes.
        
        All modules (Purchase, POS, E-Commerce, Transfers, Returns, Adjustments)
        must call this function instead of touching stock quantity fields directly.
        
        Args:
            product: The product being moved
            variant: Optional product variant
            quantity: Amount to move (always positive)
            movement_type: Type of movement (from StockMovement.MovementType)
            source_branch: Branch stock is coming from (for OUT movements)
            dest_branch: Branch stock is going to (for IN movements)
            reference: External reference (invoice, order, transfer number)
            batch_number: Batch/lot number
            expiry_date: Product expiry date
            cost_price: Cost per unit (for FIFO tracking)
            notes: Additional notes
            created_by: User who created this movement
            
        Returns:
            Created StockMovement instance
            
        Raises:
            InsufficientStockError: If there's not enough stock for OUT movements
            ValueError: If quantity is invalid
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive for stock movements.")
        
        # Create the stock movement record
        movement = StockMovement.objects.create(
            product=product,
            variant=variant,
            quantity=quantity,
            movement_type=movement_type,
            source_branch=source_branch,
            dest_branch=dest_branch,
            reference=reference,
            batch_number=batch_number,
            expiry_date=expiry_date,
            cost_price=cost_price,
            notes=notes,
            created_by=created_by,
        )
        
        # Determine which branches to update based on movement type
        out_types = {
            StockMovement.MovementType.POS_SALE_OUT,
            StockMovement.MovementType.ONLINE_ORDER_OUT,
            StockMovement.MovementType.TRANSFER_OUT,
            StockMovement.MovementType.DAMAGE_OUT,
            StockMovement.MovementType.ADJUSTMENT_OUT,
        }
        in_types = {
            StockMovement.MovementType.PURCHASE_IN,
            StockMovement.MovementType.RETURN_IN,
            StockMovement.MovementType.TRANSFER_IN,
            StockMovement.MovementType.ADJUSTMENT_IN,
        }

        if movement_type in out_types:
            StockService._apply_out_movement(
                product=product,
                variant=variant,
                branch=source_branch,
                quantity=quantity,
                batch_number=batch_number,
            )
        elif movement_type in in_types:
            StockService._apply_in_movement(
                product=product,
                variant=variant,
                branch=dest_branch,
                quantity=quantity,
                batch_number=batch_number,
                expiry_date=expiry_date,
            )
        else:
            raise ValueError(f"Unknown movement type: {movement_type}")

        # Check for low stock alerts after movement
        StockService.check_and_create_alerts(product, variant, dest_branch or source_branch)

        return movement

    @staticmethod
    def _get_stock_model_for_branch(branch: Branch):
        """Return appropriate stock model based on branch type"""
        if branch.is_warehouse:
            return WarehouseStock
        return BranchStock

    @staticmethod
    def _apply_in_movement(
        *,
        product: Product,
        variant: Optional[ProductVariant],
        branch: Optional[Branch],
        quantity: Decimal,
        batch_number: str = "",
        expiry_date: Optional[date] = None
    ) -> None:
        """Handle stock increase (IN movements)"""
        if branch is None:
            return

        stock_model = StockService._get_stock_model_for_branch(branch)
        stock, _ = stock_model.objects.select_for_update().get_or_create(
            branch=branch,
            product=product,
            variant=variant,
            batch_number=batch_number or "",
            defaults={"quantity": Decimal("0"), "expiry_date": expiry_date},
        )
        stock.quantity = F('quantity') + quantity
        if expiry_date and not stock.expiry_date:
            stock.expiry_date = expiry_date
        stock.save()
        stock.refresh_from_db()

    @staticmethod
    def _apply_out_movement(
        *,
        product: Product,
        variant: Optional[ProductVariant],
        branch: Optional[Branch],
        quantity: Decimal,
        batch_number: str = ""
    ) -> None:
        """Handle stock decrease (OUT movements)"""
        if branch is None:
            return

        stock_model = StockService._get_stock_model_for_branch(branch)
        
        try:
            stock = stock_model.objects.select_for_update().get(
                branch=branch,
                product=product,
                variant=variant,
                batch_number=batch_number or "",
            )
        except stock_model.DoesNotExist:
            raise InsufficientStockError(
                f"No stock found for {product.name} at {branch.name}"
            )
        
        if stock.quantity < quantity:
            raise InsufficientStockError(
                f"Insufficient stock for {product.name} at {branch.name}. "
                f"Available: {stock.quantity}, Requested: {quantity}"
            )
        
        stock.quantity = F('quantity') - quantity
        stock.save()
        stock.refresh_from_db()

    @staticmethod
    def get_available_stock(
        product: Product,
        variant: Optional[ProductVariant],
        branch: Branch,
        batch_number: str = ""
    ) -> Decimal:
        """Get available stock quantity for a product at a branch"""
        stock_model = StockService._get_stock_model_for_branch(branch)
        
        try:
            stock = stock_model.objects.get(
                branch=branch,
                product=product,
                variant=variant,
                batch_number=batch_number or "",
            )
            return stock.quantity
        except stock_model.DoesNotExist:
            return Decimal("0")

    @staticmethod
    def check_and_create_alerts(
        product: Product,
        variant: Optional[ProductVariant],
        branch: Branch
    ) -> None:
        """Check stock levels and create alerts if needed"""
        stock_model = StockService._get_stock_model_for_branch(branch)
        
        stocks = stock_model.objects.filter(
            branch=branch,
            product=product,
            variant=variant
        )
        
        for stock in stocks:
            # Check for low stock
            if stock.is_low_stock():
                StockAlert.objects.get_or_create(
                    product=product,
                    variant=variant,
                    branch=branch,
                    alert_type=StockAlert.AlertType.LOW_STOCK,
                    is_resolved=False,
                    defaults={
                        'current_quantity': stock.quantity
                    }
                )
            
            # Check for expiring soon
            if stock.is_expiring_soon():
                StockAlert.objects.get_or_create(
                    product=product,
                    variant=variant,
                    branch=branch,
                    alert_type=StockAlert.AlertType.EXPIRING_SOON,
                    is_resolved=False,
                    defaults={
                        'current_quantity': stock.quantity,
                        'expiry_date': stock.expiry_date
                    }
                )

    @staticmethod
    @transaction.atomic
    def transfer_stock(
        *,
        product: Product,
        variant: Optional[ProductVariant],
        quantity: Decimal,
        source_branch: Branch,
        dest_branch: Branch,
        reference: str,
        created_by: Optional[User] = None
    ) -> tuple[StockMovement, StockMovement]:
        """
        Transfer stock between branches (creates two movements: OUT and IN)
        """
        # First, remove from source
        out_movement = StockService.apply_stock_movement(
            product=product,
            variant=variant,
            quantity=quantity,
            movement_type=StockMovement.MovementType.TRANSFER_OUT,
            source_branch=source_branch,
            reference=reference,
            created_by=created_by
        )
        
        # Then, add to destination
        in_movement = StockService.apply_stock_movement(
            product=product,
            variant=variant,
            quantity=quantity,
            movement_type=StockMovement.MovementType.TRANSFER_IN,
            dest_branch=dest_branch,
            reference=reference,
            created_by=created_by
        )
        
        return out_movement, in_movement


# Export main function for backwards compatibility
apply_stock_movement = StockService.apply_stock_movement


