from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .forms import UserRegistrationForm, ProfileForm
from .models import User


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserRegistrationForm()

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    error_message = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        error_message = "Invalid email or password."

    return render(
        request,
        "users/login.html",
        {"error_message": error_message},
    )


def logout_view(request):
    logout(request)
    return redirect("users:login")


@login_required
def profile_view(request):
    return render(
        request,
        "users/profile.html",
        {"profile": request.user.profile},
    )


@login_required
def edit_profile_view(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()
            return redirect("users:profile")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form},
    )


def public_profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    return render(
        request,
        "users/public_profile.html",
        {
            "profile_user": profile_user,
            "profile": profile_user.profile,
        },
    )
