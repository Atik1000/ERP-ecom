from django.contrib import admin
from .models import (
    ShippingAddress, Cart, CartItem, OnlineOrder, 
    OrderItem, Wishlist, WishlistItem, ProductReview
)


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = [
        "full_name",
        "user",
        "city",
        "phone",
        "is_default",
        "created_at"
    ]
    list_filter = ["is_default", "city", "country"]
    search_fields = ["full_name", "user__username", "phone", "city"]
    readonly_fields = ["created_at"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "cart",
        "product",
        "variant",
        "quantity"
    ]
    search_fields = ["cart__user__username", "product__name"]


@admin.register(OnlineOrder)
class OnlineOrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "customer",
        "status",
        "payment_status"
    ]
    list_filter = ["status", "payment_status"]
    search_fields = ["order_number", "customer__username", "customer__email"]
    readonly_fields = ["order_number", "created_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "order",
        "product",
        "variant",
        "quantity",
        "unit_price"
    ]
    list_filter = ["order__status"]
    search_fields = ["product__name", "order__order_number"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ["wishlist", "product", "variant", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["wishlist__user__username", "product__name"]
    readonly_fields = ["added_at"]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "user",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at"
    ]
    list_filter = ["rating", "is_verified_purchase", "is_approved", "created_at"]
    search_fields = ["product__name", "user__username", "review_text"]
    readonly_fields = ["created_at"]
    actions = ["approve_reviews", "reject_reviews"]
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"{updated} reviews rejected.")
    reject_reviews.short_description = "Reject selected reviews"
