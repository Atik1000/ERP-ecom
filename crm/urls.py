from django.urls import path
from . import views

app_name = "crm"

urlpatterns = [
    # Customer Groups
    path("groups/", views.groups_list, name="groups_list"),
    path("groups/create/", views.create_group, name="create_group"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    
    # Loyalty Points
    path("loyalty/", views.loyalty_dashboard, name="loyalty_dashboard"),
    path("loyalty/<int:customer_id>/", views.customer_loyalty, name="customer_loyalty"),
    
    # Coupons
    path("coupons/", views.coupons_list, name="coupons_list"),
    path("coupons/create/", views.create_coupon, name="create_coupon"),
    path("coupons/<int:pk>/", views.coupon_detail, name="coupon_detail"),
    
    # Feedback
    path("feedback/", views.feedback_list, name="feedback_list"),
    path("feedback/<int:pk>/", views.feedback_detail, name="feedback_detail"),
    path("feedback/<int:pk>/respond/", views.respond_feedback, name="respond_feedback"),
    
    # Newsletter
    path("newsletter/", views.newsletter_list, name="newsletter_list"),
]
