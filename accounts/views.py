from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    return render(request, "accounts/profile.html")


