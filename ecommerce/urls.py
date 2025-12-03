from django.urls import path
from . import views

app_name = "ecommerce"

urlpatterns = [
    # E-commerce Homepage & Product Browsing
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/category/<int:category_id>/", views.products_by_category, name="products_by_category"),
    path("products/search/", views.product_search, name="product_search"),
    
    # Shopping Cart
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    
    # Checkout
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/confirm/", views.confirm_order, name="confirm_order"),
    path("orders/success/<str:order_number>/", views.order_success, name="order_success"),
    
    # Customer Orders
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("my-orders/<int:pk>/cancel/", views.cancel_order, name="cancel_order"),
    
    # Wishlist
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:item_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    
    # Reviews
    path("products/<int:product_id>/review/", views.add_review, name="add_review"),
    
    # Shipping Addresses
    path("addresses/", views.addresses_list, name="addresses_list"),
    path("addresses/create/", views.create_address, name="create_address"),
    path("addresses/<int:pk>/edit/", views.edit_address, name="edit_address"),
    path("addresses/<int:pk>/delete/", views.delete_address, name="delete_address"),
]
