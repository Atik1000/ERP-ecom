from __future__ import annotations

from typing import Optional

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Branch, BranchUserAssignment, User


class LoginForm(AuthenticationForm):
    """
    Custom login form that optionally lets staff pick an active branch.
    Customers will usually log in via the e‑commerce frontend later.
    """

    active_branch = forms.ModelChoiceField(
        queryset=Branch.objects.none(),
        required=False,
        label="Branch",
        help_text="Select the branch you are working in.",
    )

    def __init__(self, request=None, *args, **kwargs) -> None:
        super().__init__(request, *args, **kwargs)
        # Narrow branch choices based on username if possible
        username: Optional[str] = None
        data = self.data or None
        if data:
            username = data.get(self.username_field)

        branch_qs = Branch.objects.filter(is_active=True)
        if username:
            user = User.objects.filter(username=username).first()
            if user:
                # If user has explicit branch assignments, use those
                assigned_branch_ids = BranchUserAssignment.objects.filter(
                    user=user
                ).values_list("branch_id", flat=True)
                if assigned_branch_ids:
                    branch_qs = branch_qs.filter(id__in=assigned_branch_ids)

        self.fields["active_branch"].queryset = branch_qs.order_by("name")


