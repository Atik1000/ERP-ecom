from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SupplierForm
from .models import Supplier


@login_required
def purchase_dashboard(request: HttpRequest) -> HttpResponse:
    return redirect("purchase:supplier_list")


@login_required
def supplier_list(request: HttpRequest) -> HttpResponse:
    qs = Supplier.objects.all()
    q = request.GET.get("q") or ""
    if q:
        qs = qs.filter(
            Q(name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
        )

    paginator = Paginator(qs, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": q,
        "create_form": SupplierForm(),
    }
    return render(request, "purchase/supplier_list.html", context)


@login_required
def supplier_detail(request: HttpRequest, pk: int) -> HttpResponse:
    supplier = get_object_or_404(Supplier, pk=pk)
    return render(request, "purchase/supplier_detail.html", {"supplier": supplier})


@login_required
def supplier_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier created successfully.")
            return redirect("purchase:supplier_list")
    else:
        form = SupplierForm()
    return render(request, "purchase/supplier_form.html", {"form": form})


@login_required
def supplier_update(request: HttpRequest, pk: int) -> HttpResponse:
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect("purchase:supplier_list")
    else:
        form = SupplierForm(instance=supplier)
    return render(
        request,
        "purchase/supplier_form.html",
        {"form": form, "supplier": supplier},
    )


@login_required
def supplier_delete(request: HttpRequest, pk: int) -> HttpResponse:
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        supplier.delete()
        messages.success(request, "Supplier deleted.")
        return redirect("purchase:supplier_list")
    return render(request, "purchase/supplier_confirm_delete.html", {"supplier": supplier})


