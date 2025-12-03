from django.urls import path
from . import views

app_name = "pos"

urlpatterns = [
    # POS Interface
    path("", views.pos_interface, name="interface"),
    path("session/open/", views.open_session, name="open_session"),
    path("session/close/", views.close_session, name="close_session"),
    path("sale/create/", views.create_sale, name="create_sale"),
    path("sales/", views.sales_list, name="sales_list"),
    path("sales/<int:pk>/", views.sale_detail, name="sale_detail"),
]
