from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


@login_required
def expenses_list(request: HttpRequest) -> HttpResponse:
    """List all expenses"""
    return render(request, "finance/expenses_list.html")


@login_required
def create_expense(request: HttpRequest) -> HttpResponse:
    """Create a new expense"""
    return render(request, "finance/expense_form.html")


@login_required
def expense_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Expense detail"""
    return render(request, "finance/expense_detail.html")


@login_required
def approve_expense(request: HttpRequest, pk: int) -> HttpResponse:
    """Approve an expense"""
    # TODO: Implement expense approval logic
    return redirect("finance:expenses_list")


@login_required
def transactions_list(request: HttpRequest) -> HttpResponse:
    """List all transactions"""
    return render(request, "finance/transactions_list.html")


@login_required
def transaction_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Transaction detail"""
    return render(request, "finance/transaction_detail.html")


@login_required
def bank_accounts_list(request: HttpRequest) -> HttpResponse:
    """List all bank accounts"""
    return render(request, "finance/bank_accounts_list.html")


@login_required
def create_bank_account(request: HttpRequest) -> HttpResponse:
    """Create a new bank account"""
    return render(request, "finance/bank_account_form.html")


@login_required
def bank_account_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Bank account detail"""
    return render(request, "finance/bank_account_detail.html")


@login_required
def cash_reports_list(request: HttpRequest) -> HttpResponse:
    """List all daily cash reports"""
    return render(request, "finance/cash_reports_list.html")


@login_required
def create_cash_report(request: HttpRequest) -> HttpResponse:
    """Create a new daily cash report"""
    return render(request, "finance/cash_report_form.html")


@login_required
def cash_report_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Daily cash report detail"""
    return render(request, "finance/cash_report_detail.html")
