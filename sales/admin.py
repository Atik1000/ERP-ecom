from django.contrib import admin
from .models import SalesReturn, SalesReturnItem, SalesTarget


@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = [
        "return_number",
        "return_type",
        "customer",
        "branch",
        "status",
        "created_at"
    ]
    list_filter = ["return_type", "status", "branch", "created_at"]
    search_fields = ["return_number", "reference_number", "customer__username"]
    readonly_fields = ["return_number", "created_at", "processed_at"]
    actions = ["approve_returns", "reject_returns"]
    
    def approve_returns(self, request, queryset):
        updated = queryset.filter(status="pending").update(
            status="approved",
            processed_by=request.user
        )
        self.message_user(request, f"{updated} returns approved.")
    approve_returns.short_description = "Approve selected returns"
    
    def reject_returns(self, request, queryset):
        updated = queryset.filter(status="pending").update(
            status="rejected",
            processed_by=request.user
        )
        self.message_user(request, f"{updated} returns rejected.")
    reject_returns.short_description = "Reject selected returns"


@admin.register(SalesReturnItem)
class SalesReturnItemAdmin(admin.ModelAdmin):
    list_display = [
        "sales_return",
        "product",
        "variant",
        "quantity",
        "unit_price"
    ]
    list_filter = ["sales_return__status", "sales_return__return_type"]
    search_fields = ["product__name", "sales_return__return_number"]


@admin.register(SalesTarget)
class SalesTargetAdmin(admin.ModelAdmin):
    list_display = [
        "target_type",
        "branch",
        "user",
        "target_amount",
        "achieved_amount"
    ]
    list_filter = ["target_type", "branch"]
    search_fields = ["branch__name", "user__username"]
