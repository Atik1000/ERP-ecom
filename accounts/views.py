from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm
from .models import Branch


class BranchAwareLoginView(LoginView):
    """
    Custom LoginView that stores the selected active branch in the session.
    Role-based redirects:
    - Customers → E-commerce homepage (/)
    - Staff (Admin, Managers, Cashiers) → Dashboard (/dashboard)
    """

    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        """Redirect based on user role"""
        user = self.request.user
        
        # Customer users go to e-commerce homepage
        if user.role == "customer":
            return "/"  # E-commerce homepage
        
        # All staff members go to dashboard
        return "/dashboard/"

    def form_valid(self, form: LoginForm) -> HttpResponse:
        response = super().form_valid(form)
        active_branch = form.cleaned_data.get("active_branch")
        if active_branch:
            self.request.session["active_branch_id"] = active_branch.id
        else:
            # Fall back to user's default branch if set
            user = self.request.user
            if getattr(user, "default_branch_id", None):
                self.request.session["active_branch_id"] = user.default_branch_id
        return response


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    active_branch_id = request.session.get("active_branch_id")
    active_branch = None
    if active_branch_id:
        active_branch = Branch.objects.filter(id=active_branch_id).first()
    context = {"active_branch": active_branch}
    return render(request, "accounts/profile.html", context)


@login_required
def switch_branch(request: HttpRequest) -> HttpResponse:
    """
    Simple endpoint to switch the active branch from a dropdown in the navbar/sidebar.
    """
    if request.method == "POST":
        branch_id = request.POST.get("branch_id")
        if branch_id:
            branch = Branch.objects.filter(id=branch_id, is_active=True).first()
            if branch:
                request.session["active_branch_id"] = branch.id
                messages.success(request, f"Switched to branch: {branch}")
            else:
                messages.error(request, "Invalid branch selected.")
        return redirect(request.POST.get("next") or reverse_lazy("dashboard"))
    return redirect("dashboard")

