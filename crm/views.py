from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


@login_required
def groups_list(request: HttpRequest) -> HttpResponse:
    """List all customer groups"""
    return render(request, "crm/groups_list.html")


@login_required
def create_group(request: HttpRequest) -> HttpResponse:
    """Create a new customer group"""
    return render(request, "crm/group_form.html")


@login_required
def group_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Customer group detail"""
    return render(request, "crm/group_detail.html")


@login_required
def loyalty_dashboard(request: HttpRequest) -> HttpResponse:
    """Loyalty points dashboard"""
    return render(request, "crm/loyalty_dashboard.html")


@login_required
def customer_loyalty(request: HttpRequest, customer_id: int) -> HttpResponse:
    """Customer loyalty points detail"""
    return render(request, "crm/customer_loyalty.html")


@login_required
def coupons_list(request: HttpRequest) -> HttpResponse:
    """List all coupons"""
    return render(request, "crm/coupons_list.html")


@login_required
def create_coupon(request: HttpRequest) -> HttpResponse:
    """Create a new coupon"""
    return render(request, "crm/coupon_form.html")


@login_required
def coupon_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Coupon detail"""
    return render(request, "crm/coupon_detail.html")


@login_required
def feedback_list(request: HttpRequest) -> HttpResponse:
    """List all customer feedback"""
    return render(request, "crm/feedback_list.html")


@login_required
def feedback_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Feedback detail"""
    return render(request, "crm/feedback_detail.html")


@login_required
def respond_feedback(request: HttpRequest, pk: int) -> HttpResponse:
    """Respond to customer feedback"""
    # TODO: Implement feedback response logic
    return redirect("crm:feedback_list")


@login_required
def newsletter_list(request: HttpRequest) -> HttpResponse:
    """List all newsletter subscribers"""
    return render(request, "crm/newsletter_list.html")
