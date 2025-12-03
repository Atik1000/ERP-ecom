from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django Admin Panel
    path("admin/", admin.site.urls),
    
    # E-commerce Frontend (Public - Customer facing)
    path("", include("ecommerce.urls", namespace="ecommerce")),  # Base route for e-commerce
    
    # Authentication
    path("accounts/", include("accounts.urls", namespace="accounts")),
    
    # Admin Dashboard & Modules (Staff only - Role-based)
    path("dashboard/", include("reports.urls", namespace="dashboard")),  # Main dashboard
    path("dashboard/inventory/", include("inventory.urls", namespace="inventory")),
    path("dashboard/purchase/", include("purchase.urls", namespace="purchase")),
    path("dashboard/pos/", include("pos.urls", namespace="pos")),
    path("dashboard/sales/", include("sales.urls", namespace="sales")),
    path("dashboard/finance/", include("finance.urls", namespace="finance")),
    path("dashboard/crm/", include("crm.urls", namespace="crm")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


