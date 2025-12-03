from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from decimal import Decimal

from .models import (
    ShippingAddress, Cart, CartItem, OnlineOrder,
    OrderItem, Wishlist, WishlistItem, ProductReview
)
from inventory.models import Product, ProductVariant, Category


# E-commerce Homepage
def home(request: HttpRequest) -> HttpResponse:
    """E-commerce homepage with featured products"""
    featured_products = Product.objects.filter(is_active=True)[:8]
    categories = Category.objects.filter(is_active=True)
    
    context = {
        "featured_products": featured_products,
        "categories": categories,
    }
    return render(request, "ecommerce/home.html", context)


# Product Listing & Detail
def product_list(request: HttpRequest) -> HttpResponse:
    """Product listing with filtering and search"""
    products = Product.objects.filter(is_active=True)
    
    # Filter by category
    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search
    query = request.GET.get("q")
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        "page_obj": page_obj,
        "categories": categories,
        "current_category": category_id,
        "query": query,
    }
    return render(request, "ecommerce/product_list.html", context)


def product_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Product detail page with reviews"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = ProductReview.objects.filter(product=product, is_approved=True)
    
    context = {
        "product": product,
        "reviews": reviews,
    }
    return render(request, "ecommerce/product_detail.html", context)


def products_by_category(request: HttpRequest, category_id: int) -> HttpResponse:
    """Products filtered by category"""
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(category=category, is_active=True)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "ecommerce/category_products.html", context)


def product_search(request: HttpRequest) -> HttpResponse:
    """Product search results"""
    query = request.GET.get("q", "")
    products = Product.objects.filter(
        Q(name__icontains=query) | 
        Q(description__icontains=query),
        is_active=True
    )
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "query": query,
        "page_obj": page_obj,
    }
    return render(request, "ecommerce/search_results.html", context)


# Shopping Cart
@login_required
def cart_view(request: HttpRequest) -> HttpResponse:
    """View shopping cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    context = {
        "cart": cart,
    }
    return render(request, "ecommerce/cart.html", context)


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """Add product to cart"""
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id, is_active=True)
        quantity = int(request.POST.get("quantity", 1))
        variant_id = request.POST.get("variant_id")
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant_id=variant_id,
            defaults={"quantity": quantity, "unit_price": product.selling_price}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f"{product.name} added to cart!")
        return redirect("ecommerce:cart")
    
    return redirect("ecommerce:home")


@login_required
def update_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    """Update cart item quantity"""
    if request.method == "POST":
        cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
        quantity = int(request.POST.get("quantity", 1))
        
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated!")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from cart!")
        
        return redirect("ecommerce:cart")
    
    return redirect("ecommerce:cart")


@login_required
def remove_from_cart(request: HttpRequest, item_id: int) -> HttpResponse:
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart!")
    return redirect("ecommerce:cart")


# Checkout
@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """Checkout page"""
    cart = get_object_or_404(Cart, user=request.user)
    
    if cart.items.count() == 0:
        messages.warning(request, "Your cart is empty!")
        return redirect("ecommerce:cart")
    
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        "cart": cart,
        "addresses": addresses,
    }
    return render(request, "ecommerce/checkout.html", context)


@login_required
def confirm_order(request: HttpRequest) -> HttpResponse:
    """Confirm and create order"""
    if request.method == "POST":
        # TODO: Implement order creation logic
        messages.success(request, "Order placed successfully!")
        return redirect("ecommerce:home")
    
    return redirect("ecommerce:checkout")


@login_required
def order_success(request: HttpRequest, order_number: str) -> HttpResponse:
    """Order confirmation page"""
    order = get_object_or_404(OnlineOrder, order_number=order_number, customer=request.user)
    
    context = {
        "order": order,
    }
    return render(request, "ecommerce/order_success.html", context)


# Customer Orders
@login_required
def my_orders(request: HttpRequest) -> HttpResponse:
    """Customer's order history"""
    orders = OnlineOrder.objects.filter(customer=request.user).order_by("-order_date")
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    context = {
        "page_obj": page_obj,
    }
    return render(request, "ecommerce/my_orders.html", context)


@login_required
def order_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Order detail page"""
    order = get_object_or_404(OnlineOrder, pk=pk, customer=request.user)
    
    context = {
        "order": order,
    }
    return render(request, "ecommerce/order_detail.html", context)


@login_required
def cancel_order(request: HttpRequest, pk: int) -> HttpResponse:
    """Cancel order"""
    order = get_object_or_404(OnlineOrder, pk=pk, customer=request.user)
    
    if order.status in ["pending", "confirmed"]:
        order.status = "cancelled"
        order.save()
        messages.success(request, "Order cancelled successfully!")
    else:
        messages.error(request, "This order cannot be cancelled!")
    
    return redirect("ecommerce:order_detail", pk=pk)


# Wishlist
@login_required
def wishlist_view(request: HttpRequest) -> HttpResponse:
    """View wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    context = {
        "wishlist": wishlist,
    }
    return render(request, "ecommerce/wishlist.html", context)


@login_required
def add_to_wishlist(request: HttpRequest, product_id: int) -> HttpResponse:
    """Add product to wishlist"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    messages.success(request, f"{product.name} added to wishlist!")
    return redirect(request.META.get("HTTP_REFERER", "ecommerce:home"))


@login_required
def remove_from_wishlist(request: HttpRequest, item_id: int) -> HttpResponse:
    """Remove item from wishlist"""
    wishlist_item = get_object_or_404(WishlistItem, pk=item_id, wishlist__user=request.user)
    wishlist_item.delete()
    messages.success(request, "Item removed from wishlist!")
    return redirect("ecommerce:wishlist")


# Reviews
@login_required
def add_review(request: HttpRequest, product_id: int) -> HttpResponse:
    """Add product review"""
    if request.method == "POST":
        product = get_object_or_404(Product, pk=product_id)
        rating = int(request.POST.get("rating", 5))
        review_text = request.POST.get("review_text", "")
        
        ProductReview.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            review_text=review_text
        )
        
        messages.success(request, "Review submitted! It will be visible after approval.")
        return redirect("ecommerce:product_detail", pk=product_id)
    
    return redirect("ecommerce:home")


# Shipping Addresses
@login_required
def addresses_list(request: HttpRequest) -> HttpResponse:
    """List all shipping addresses"""
    addresses = ShippingAddress.objects.filter(user=request.user)
    
    context = {
        "addresses": addresses,
    }
    return render(request, "ecommerce/addresses_list.html", context)


@login_required
def create_address(request: HttpRequest) -> HttpResponse:
    """Create new shipping address"""
    if request.method == "POST":
        # TODO: Implement address creation with form
        messages.success(request, "Address created successfully!")
        return redirect("ecommerce:addresses_list")
    
    return render(request, "ecommerce/address_form.html")


@login_required
def edit_address(request: HttpRequest, pk: int) -> HttpResponse:
    """Edit shipping address"""
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    
    if request.method == "POST":
        # TODO: Implement address update with form
        messages.success(request, "Address updated successfully!")
        return redirect("ecommerce:addresses_list")
    
    context = {
        "address": address,
    }
    return render(request, "ecommerce/address_form.html", context)


@login_required
def delete_address(request: HttpRequest, pk: int) -> HttpResponse:
    """Delete shipping address"""
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "Address deleted successfully!")
    return redirect("ecommerce:addresses_list")
