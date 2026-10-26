from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render

from notifications.emails import send_welcome_email

from .forms import RegisterForm


def register(request):
    """Show the sign-up form and create the account (US-01).

    People who are already logged in are sent to the home page (US-03).
    """
    if request.user.is_authenticated:
        return redirect("home:index")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_welcome_email(user)
            messages.success(request, f"Welcome, {user.username}! Your account is ready.")
            return redirect("home:index")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


class SiteLoginView(SuccessMessageMixin, LoginView):
    """Django's built-in login page, with a welcome message (US-02)."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    success_message = "Welcome back, %(username)s!"
