from django.contrib import admin
from .models import (
    CustomerGroup, CustomerGroupMembership, LoyaltyPoints,
    Coupon, CouponUsage, Feedback, Newsletter
)


@admin.register(CustomerGroup)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "discount_percent",
        "points_multiplier",
        "is_active",
        "get_member_count",
        "created_at"
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    readonly_fields = ["created_at"]
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = "Members"


@admin.register(CustomerGroupMembership)
class CustomerGroupMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "group", "joined_at"]
    list_filter = ["group", "joined_at"]
    search_fields = ["user__username", "user__email", "group__name"]
    readonly_fields = ["joined_at"]


@admin.register(LoyaltyPoints)
class LoyaltyPointsAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "points",
        "transaction_type",
        "reference",
        "created_at"
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = ["user__username", "reference"]
    readonly_fields = ["created_at", "balance_after"]
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Transaction Info", {
            "fields": ("user", "points", "transaction_type", "balance_after")
        }),
        ("Reference", {
            "fields": ("reference", "description", "expires_at")
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "discount_type",
        "value",
        "min_purchase_amount",
        "used_count",
        "max_uses",
        "valid_from",
        "valid_to",
        "is_active"
    ]
    list_filter = ["discount_type", "is_active", "valid_from", "valid_to"]
    search_fields = ["code", "description"]
    readonly_fields = ["created_at", "used_count", "updated_at"]
    date_hierarchy = "valid_from"
    filter_horizontal = ["applicable_products", "customer_groups"]
    actions = ["activate_coupons", "deactivate_coupons"]
    
    fieldsets = (
        ("Coupon Info", {
            "fields": ("code", "description", "is_active")
        }),
        ("Discount", {
            "fields": ("discount_type", "value")
        }),
        ("Restrictions", {
            "fields": (
                "min_purchase_amount",
                "applicable_products",
                "customer_groups"
            )
        }),
        ("Usage", {
            "fields": ("max_uses", "per_user_limit", "used_count")
        }),
        ("Validity", {
            "fields": ("valid_from", "valid_to")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at")
        }),
    )
    
    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} coupons activated.")
    activate_coupons.short_description = "Activate selected coupons"
    
    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} coupons deactivated.")
    deactivate_coupons.short_description = "Deactivate selected coupons"


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = [
        "coupon",
        "user",
        "order_reference",
        "discount_amount",
        "used_at"
    ]
    list_filter = ["used_at", "coupon"]
    search_fields = ["coupon__code", "user__username", "order_reference"]
    readonly_fields = ["used_at"]
    date_hierarchy = "used_at"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "order_reference",
        "rating",
        "is_published",
        "created_at"
    ]
    list_filter = ["is_published", "rating", "created_at"]
    search_fields = ["user__username", "order_reference", "comment"]
    readonly_fields = ["created_at"]
    actions = ["publish_feedback", "unpublish_feedback"]
    
    fieldsets = (
        ("Feedback Info", {
            "fields": ("user", "order_reference", "rating", "comment")
        }),
        ("Status", {
            "fields": ("is_published", "admin_response")
        }),
        ("Metadata", {
            "fields": ("created_at",)
        }),
    )
    
    def publish_feedback(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} feedback published.")
    publish_feedback.short_description = "Publish selected feedback"
    
    def unpublish_feedback(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} feedback unpublished.")
    unpublish_feedback.short_description = "Unpublish selected feedback"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "is_active",
        "subscribed_at",
        "unsubscribed_at"
    ]
    list_filter = ["is_active", "subscribed_at"]
    search_fields = ["email"]
    readonly_fields = ["subscribed_at", "unsubscribed_at"]
    actions = ["activate_subscriptions", "deactivate_subscriptions"]
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f"{updated} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f"{updated} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
