from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from movies.models.movie_model import Favorite, Review  # Import models
from django.contrib import messages
from movies.models.auth_model import UserProfile, User
from django.contrib.auth import update_session_auth_hash,authenticate
from django.http import JsonResponse

@login_required
def profile_view(request):
    """User Profile Page"""
    user = request.user  # ✅ Get logged-in user

    # ✅ Get favorite movies of the user
    favorite_movies = Favorite.objects.filter(user=user).select_related("movie")

    # ✅ Get recently reviewed movies
    recent_reviews = Review.objects.filter(user=user).select_related("movie").order_by("-created_at")[:5]

    context = {
        "user": user,
        "favorite_movies": favorite_movies,
        "recent_reviews": recent_reviews,
    }
    return render(request, "movies/profile.html", context)


@login_required
def settings_view(request):
    """Display user profile information"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    return render(request, "movies/settings.html", {
        "user_profile": user_profile,
        "user": request.user
    })

@login_required
def change_password(request):
    """Allow users to change their password"""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")

        if request.user.check_password(current_password):
            request.user.set_password(new_password)
            request.user.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, request.user)

            messages.success(request, "Your password has been updated successfully!")
        else:
            messages.error(request, "Current password is incorrect!")

    return redirect("settings")

