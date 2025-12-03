from __future__ import annotations

from django.db import models


class PosReturn(models.Model):
    """
    Simple POS return record; links back to a POS sale by ID.
    (We avoid direct FK to prevent circular imports; can be refined later.)
    """

    pos_sale_id = models.IntegerField(help_text="ID of the related PosSale")
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"POS Return #{self.id} for sale {self.pos_sale_id}"



