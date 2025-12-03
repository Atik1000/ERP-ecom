from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    # Sales Returns
    path("returns/", views.returns_list, name="returns_list"),
    path("returns/create/", views.create_return, name="create_return"),
    path("returns/<int:pk>/", views.return_detail, name="return_detail"),
    path("returns/<int:pk>/approve/", views.approve_return, name="approve_return"),
    
    # Sales Targets
    path("targets/", views.targets_list, name="targets_list"),
    path("targets/create/", views.create_target, name="create_target"),
    path("targets/<int:pk>/", views.target_detail, name="target_detail"),
]
