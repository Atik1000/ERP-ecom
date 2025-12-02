from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.db import transaction

from accounts.models import Branch, User
from inventory.models import (
    BranchStock,
    Product,
    ProductVariant,
    StockMovement,
    WarehouseStock,
)


@transaction.atomic
def apply_stock_movement(
    *,
    product: Product,
    variant: Optional[ProductVariant],
    quantity: Decimal,
    movement_type: str,
    source_branch: Optional[Branch] = None,
    dest_branch: Optional[Branch] = None,
    reference: str = "",
    created_by: Optional[User] = None,
) -> StockMovement:
    """
    Central service for all stock changes.

    All modules (Purchase, POS, E‑Commerce, Transfers, Returns, Adjustments)
    must call this function instead of touching stock quantity fields directly.
    """
    if quantity <= 0:
        raise ValueError("Quantity must be positive for stock movements.")

    movement = StockMovement.objects.create(
        product=product,
        variant=variant,
        quantity=quantity,
        movement_type=movement_type,
        source_branch=source_branch,
        dest_branch=dest_branch,
        reference=reference,
        created_by=created_by,
    )

    # Determine sign based on movement type
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
        _apply_out_movement(
            product=product,
            variant=variant,
            branch=source_branch,
            quantity=quantity,
        )
    elif movement_type in in_types:
        _apply_in_movement(
            product=product,
            variant=variant,
            branch=dest_branch,
            quantity=quantity,
        )
    else:
        raise ValueError(f"Unknown movement type: {movement_type}")

    return movement


def _get_stock_model_for_branch(branch: Branch):
    if branch.is_warehouse:
        return WarehouseStock
    return BranchStock


def _apply_in_movement(
    *, product: Product, variant: Optional[ProductVariant], branch: Optional[Branch], quantity: Decimal
) -> None:
    if branch is None:
        # For some IN types (like initial load) we may not yet target a branch.
        return

    stock_model = _get_stock_model_for_branch(branch)
    stock, _ = stock_model.objects.select_for_update().get_or_create(
        branch=branch,
        product=product,
        variant=variant,
        defaults={"quantity": Decimal("0")},
    )
    stock.quantity += quantity
    stock.save(update_fields=["quantity"])


def _apply_out_movement(
    *, product: Product, variant: Optional[ProductVariant], branch: Optional[Branch], quantity: Decimal
) -> None:
    if branch is None:
        return

    stock_model = _get_stock_model_for_branch(branch)
    stock, _ = stock_model.objects.select_for_update().get_or_create(
        branch=branch,
        product=product,
        variant=variant,
        defaults={"quantity": Decimal("0")},
    )
    new_qty = stock.quantity - quantity
    if new_qty < 0:
        # Future enhancement: configurable behavior for negative stock.
        new_qty = Decimal("0")
    stock.quantity = new_qty
    stock.save(update_fields=["quantity"])


