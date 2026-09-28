from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from movies.forms import RegisterForm
from django.contrib import messages
from django.contrib.messages import get_messages

def register(request):
    """User Registration with Password Hashing Fix"""
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()  # This saves the user and creates the UserProfile
            messages.success(request, "Registration successful!")
            return redirect("login")
        else:
            # Show specific error messages from form
            errors = form.errors.as_text()
            messages.error(request, f"Registration failed: {errors}")

    else:
        form = RegisterForm()

    # Consume leftover messages to prevent stacking
    get_messages(request)
    return render(request, "movies/register.html", {"form": form})

def user_login(request):
    """User Login Debugging"""
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")

    if request.method == "POST":
        login_input = request.POST.get("login_input")  # ✅ Can be username or email
        password = request.POST.get("password")

        # ✅ Debugging: Print values received from the form
        print(f"🟡 Received login input: {login_input}")
        print(f"🟡 Received password: {password}")

        # ✅ Debugging: Check if user exists
        user_by_username = User.objects.filter(username=login_input).first()
        user_by_email = User.objects.filter(email=login_input).first()
        print(f"🔍 User by username: {user_by_username}")
        print(f"🔍 User by email: {user_by_email}")

        user = user_by_username or user_by_email

        if user:
            # ✅ Debugging: Check if authentication works
            auth_user = authenticate(request, username=user.username, password=password)
            print(f"🔍 Authenticated user: {auth_user}")

            if auth_user:
                login(request, auth_user)
                messages.success(request, "Login successful!")
                return redirect("home")
            else:
                messages.error(request, "Invalid password. Please try again.")  # Wrong password
        else:
            # No user found - check if it was email or username and provide specific message
            if '@' in str(login_input):
                messages.error(request, "No account found with this email address. Please check your email or register a new account.")
            else:
                messages.error(request, "No account found with this username. Please check your username or register a new account.")

    # Consume any leftover messages so they don't accumulate
    get_messages(request)
    return render(request, "movies/login.html")

def user_logout(request):
    """Handles user logout and redirects to the homepage."""
    # Only log out if the user is actually authenticated (not admin session only)
    if request.user.is_authenticated:
        logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")