from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from movies.forms import RegisterForm
from django.contrib import messages

def register(request):
    """User Registration with Password Hashing Fix"""
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # ✅ Don't save immediately
            user.set_password(form.cleaned_data["password1"])  # ✅ Hash password manually
            user.save()
            messages.success(request, "Registration successful!")
            return redirect("login")
        else:
            print("🚨 Registration Form Errors:", form.errors)  # ✅ Debugging step
            messages.error(request, "Error in registration. Please check the form.")

    else:
        form = RegisterForm()

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
                messages.error(request, "Incorrect password.")  # ✅ Wrong password
        else:
            messages.error(request, "No account found with that username or email.")  # ✅ User does not exist

    return render(request, "movies/login.html")

def user_logout(request):
    """Handles user logout and redirects to the homepage."""
    logout(request)  # ✅ Log out the user
    messages.success(request, "You have been logged out successfully.")  # ✅ Display success message
    return redirect("home")  # ✅ Redirect to home page instead of login page