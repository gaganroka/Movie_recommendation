from django.shortcuts import render,  get_object_or_404,redirect
from movies.models.movie_model import *
from django.http import JsonResponse
import random
from movies.forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from movies.utils.recommendation_utils import *

def home_view(request):
    """Display movie recommendations using Content-Based & Collaborative Filtering."""

    # ✅ Build similarity matrix once
    data, similarity_matrix = build_movie_similarity_matrix()

    # ✅ Default: Show 20 random movies
    all_movies = list(Movie.objects.all())
    random_movies = random.sample(all_movies, min(len(all_movies), 20))

    # ✅ Check if user is logged in
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user).select_related("movie")

        # ✅ If user has favorites, generate recommendations
        if user_favorites.exists():
            content_based_recommendations = set()
            total_favorites = user_favorites.count()

            for favorite in user_favorites:
                movie = favorite.movie
                # ✅ Fetch similar movies from Content-Based Filtering
                similar_movies = get_similar_movies(movie.id, data, similarity_matrix, num_recommendations=20 // total_favorites)
                content_based_recommendations.update(similar_movies)

            # ✅ Get Collaborative Filtering recommendations
            collaborative_recommendations = recommend_movies_for_user(request.user.id, num_recommendations=10)

            return render(request, "movies/home.html", {
                "content_based_recommendations": list(content_based_recommendations),
                "collaborative_recommendations": list(collaborative_recommendations),
                "random_movies": None,  # Hide random movies when recommendations exist
            })

    # ✅ If user is not logged in OR has no favorites, show 20 random movies
    return render(request, "movies/home.html", {
        "content_based_recommendations": None,  # Hide "For You" when no recommendations exist
        "collaborative_recommendations": None,  # Hide collaborative filtering
        "random_movies": random_movies,  # Display 20 random movies
    })

def movie_detail(request, movie_id):
    # Fetch the selected movie
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = movie.reviews.all().order_by("-created_at")  # Get reviews for the movie

    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, movie=movie).exists()

    # Fetch other movies by the same director (excluding the current movie)
    related_movies = Movie.objects.filter(director=movie.director).exclude(id=movie.id)[:5]

    return render(request, "movies/movie_detail.html", {
        "movie": movie,
        "reviews": reviews,
        "related_movies": related_movies,
        "is_favorited": is_favorited,
    })

def live_search(request):
    """API endpoint for live movie search"""
    query = request.GET.get("q", "").strip()
    
    if query:
        movies = Movie.objects.filter(title__icontains=query)[:5]  # ✅ Limit to 5 results
        results = [{"id": movie.id, "title": movie.title, "year": movie.year, "poster_url": movie.poster_url} for movie in movies]
    else:
        results = []

    return JsonResponse({"results": results})

@login_required
def submit_review(request, movie_id):
    """Allow users to submit only a rating or only a review"""
    movie = get_object_or_404(Movie, id=movie_id)

    # Check if the user has already reviewed this movie
    existing_review = Review.objects.filter(movie=movie, user=request.user).first()

    if request.method == "POST":
        rating = request.POST.get("rating")  # Can be None
        comment = request.POST.get("comment").strip()  # Can be empty

        # ✅ Allow rating-only or review-only, but prevent empty submissions
        if not rating and not comment:
            messages.error(request, "You must provide either a rating or a review.")
            return redirect("movie_detail", movie_id=movie.id)

        if existing_review:
            # ✅ Update existing review (if user already reviewed)
            if rating:
                existing_review.rating = int(rating)
            if comment:
                existing_review.comment = comment
            existing_review.save()
            messages.success(request, "Your review has been updated.")
        else:
            # ✅ Create a new review (if user hasn't reviewed)
            Review.objects.create(
                movie=movie,
                user=request.user,
                rating=int(rating) if rating else None,  # Store rating only if provided
                comment=comment if comment else ""  # Store comment only if provided
            )
            messages.success(request, "Review submitted successfully!")

    return redirect("movie_detail", movie_id=movie.id)

@login_required
def toggle_favorite(request, movie_id):
    """Add or Remove Movie from Favorites."""
    movie = get_object_or_404(Movie, id=movie_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, movie=movie)

    if not created:
        favorite.delete()  # ✅ Remove from favorites if already added
        return JsonResponse({"status": "removed"})  # ✅ Return JSON response
    else:
        return JsonResponse({"status": "added"})  # ✅ Return JSON response