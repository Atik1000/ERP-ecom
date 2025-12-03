from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    # Expenses
    path("expenses/", views.expenses_list, name="expenses_list"),
    path("expenses/create/", views.create_expense, name="create_expense"),
    path("expenses/<int:pk>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:pk>/approve/", views.approve_expense, name="approve_expense"),
    
    # Transactions
    path("transactions/", views.transactions_list, name="transactions_list"),
    path("transactions/<int:pk>/", views.transaction_detail, name="transaction_detail"),
    
    # Bank Accounts
    path("bank-accounts/", views.bank_accounts_list, name="bank_accounts_list"),
    path("bank-accounts/create/", views.create_bank_account, name="create_bank_account"),
    path("bank-accounts/<int:pk>/", views.bank_account_detail, name="bank_account_detail"),
    
    # Daily Cash Reports
    path("cash-reports/", views.cash_reports_list, name="cash_reports_list"),
    path("cash-reports/create/", views.create_cash_report, name="create_cash_report"),
    path("cash-reports/<int:pk>/", views.cash_report_detail, name="cash_report_detail"),
]
