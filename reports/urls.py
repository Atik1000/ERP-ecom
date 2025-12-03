from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Main Dashboard (Role-based)
    path("", views.dashboard, name="home"),
    
    # Reports
    path("reports/inventory/", views.inventory_report, name="inventory_report"),
    path("reports/sales/", views.sales_report, name="sales_report"),
    path("reports/purchase/", views.purchase_report, name="purchase_report"),
    path("reports/financial/", views.financial_report, name="financial_report"),
    path("reports/customer/", views.customer_report, name="customer_report"),
]
