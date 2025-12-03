from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


@login_required
def returns_list(request: HttpRequest) -> HttpResponse:
    """List all sales returns"""
    return render(request, "sales/returns_list.html")


@login_required
def create_return(request: HttpRequest) -> HttpResponse:
    """Create a new sales return"""
    return render(request, "sales/return_form.html")


@login_required
def return_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Sales return detail"""
    return render(request, "sales/return_detail.html")


@login_required
def approve_return(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve a sales return"""
    # TODO: Implement return approval logic
    return redirect("sales:returns_list")


@login_required
def targets_list(request: HttpRequest) -> HttpResponse:
    """List all sales targets"""
    return render(request, "sales/targets_list.html")


@login_required
def create_target(request: HttpRequest) -> HttpResponse:
    """Create a new sales target"""
    return render(request, "sales/target_form.html")


@login_required
def target_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Sales target detail"""
    return render(request, "sales/target_detail.html")
