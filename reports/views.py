from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.db.models import Sum, Count
from datetime import datetime, timedelta

from accounts.models import User
from inventory.models import Product, StockAlert
from pos.models import PosSale
from ecommerce.models import OnlineOrder
from purchase.models import PurchaseOrder


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """
    Main dashboard with role-based content
    - Admin: Overall system stats
    - Warehouse Manager: Stock levels, transfers
    - Branch Manager: Branch sales, inventory
    - Cashier: POS quick access
    """
    user = request.user
    
    context = {
        "user": user,
        "role": user.role,
    }
    
    # Role-based data
    if user.role == "admin":
        # Admin dashboard: Overall stats
        context.update({
            "total_products": Product.objects.count(),
            "total_orders": OnlineOrder.objects.count(),
            "total_sales": PosSale.objects.count(),
            "low_stock_alerts": StockAlert.objects.filter(is_resolved=False).count(),
            "pending_purchases": PurchaseOrder.objects.filter(status="pending").count(),
        })
        return render(request, "dashboard/admin_dashboard.html", context)
    
    elif user.role == "warehouse_manager":
        # Warehouse manager dashboard: Stock management
        context.update({
            "low_stock_alerts": StockAlert.objects.filter(is_resolved=False).count(),
            "pending_transfers": 0,  # TODO: Count pending transfers
        })
        return render(request, "dashboard/warehouse_dashboard.html", context)
    
    elif user.role == "branch_manager":
        # Branch manager dashboard: Branch operations
        branch = user.default_branch
        context.update({
            "branch": branch,
            "today_sales": PosSale.objects.filter(
                branch=branch,
                sale_date=datetime.now().date()
            ).count(),
        })
        return render(request, "dashboard/branch_dashboard.html", context)
    
    elif user.role == "cashier":
        # Cashier dashboard: POS quick access
        return render(request, "dashboard/cashier_dashboard.html", context)
    
    # Default dashboard for customers
    return render(request, "dashboard/default_dashboard.html", context)


@login_required
def inventory_report(request: HttpRequest) -> HttpResponse:
    """Inventory reports"""
    return render(request, "reports/inventory_report.html")


@login_required
def sales_report(request: HttpRequest) -> HttpResponse:
    """Sales reports"""
    return render(request, "reports/sales_report.html")


@login_required
def purchase_report(request: HttpRequest) -> HttpResponse:
    """Purchase reports"""
    return render(request, "reports/purchase_report.html")


@login_required
def financial_report(request: HttpRequest) -> HttpResponse:
    """Financial reports"""
    return render(request, "reports/financial_report.html")


@login_required
def customer_report(request: HttpRequest) -> HttpResponse:
    """Customer reports"""
    return render(request, "reports/customer_report.html")
