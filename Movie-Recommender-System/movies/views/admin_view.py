from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from movies.models.admin_model import AdminUser
from movies.models.movie_model import Movie, Review
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404


# 🔐 Decorator to protect all admin routes
def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_logged_in'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ✅ Admin Login
def admin_login(request):
    print("🔥 ADMIN LOGIN VIEW HIT")  # Add this
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin_user = AdminUser.objects.get(username=username)
            if check_password(password, admin_user.password):
                request.session['admin_logged_in'] = True
                request.session['admin_id'] = admin_user.id
                return redirect("admin_dashboard")
            else:
                messages.error(request, "Incorrect password.")
        except AdminUser.DoesNotExist:
            messages.error(request, "Admin user not found.")

    return render(request, "custom_admin/login.html")


# 🚪 Admin Logout
def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


# 🏠 Admin Dashboard
@admin_required
def admin_dashboard(request):
    admin_id = request.session.get('admin_id')
    admin_user = AdminUser.objects.get(id=admin_id)

    return render(request, "custom_admin/dashboard.html", {
        "admin_user": admin_user,
        "total_users": User.objects.count(),
        "total_movies": Movie.objects.count(),
        "total_reviews": Review.objects.count(),
    })

@admin_required
def manage_users(request):
    users = User.objects.all().order_by("id")  # Just fetch all users
    return render(request, "custom_admin/users.html", {"users": users})

# 🎬 Manage Movies
@admin_required
def manage_movies(request):
    all_movies = Movie.objects.all()
    paginator = Paginator(all_movies, 8)  # 8 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "custom_admin/movies.html", {
        "movies": page_obj
    })

@admin_required
def add_movie(request):
    if request.method == "POST":
        title = request.POST.get("title")
        year = request.POST.get("year")
        genre = request.POST.get("genre")
        director = request.POST.get("director")
        actors = request.POST.get("actors")
        plot = request.POST.get("plot")
        imdb_rating = request.POST.get("imdb_rating")
        imdb_votes = request.POST.get("imdb_votes")
        box_office = request.POST.get("box_office")
        poster_url = request.POST.get("poster_url")

        if not title or not poster_url:
            messages.error(request, "Title and poster URL are required.")
        else:
            Movie.objects.create(
                title=title,
                year=year,
                genre=genre,
                director=director,
                actors=actors,
                plot=plot,
                imdb_rating=imdb_rating,
                imdb_votes=imdb_votes,
                box_office=box_office,
                poster_url=poster_url
            )
            messages.success(request, f"Movie '{title}' added successfully.")
            return redirect("manage_movies")

    return render(request, "custom_admin/add_movie.html")

# 📝 Manage Reviews
@admin_required
def manage_reviews(request):
    reviews = Review.objects.select_related("movie", "user").all()
    return render(request, "custom_admin/reviews.html", {"reviews": reviews})

@admin_required
def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":
        movie.title = request.POST.get("title")
        movie.year = request.POST.get("year")
        movie.genre = request.POST.get("genre")
        movie.director = request.POST.get("director")
        movie.actors = request.POST.get("actors")
        movie.plot = request.POST.get("plot")
        movie.imdb_rating = request.POST.get("imdb_rating")
        movie.imdb_votes = request.POST.get("imdb_votes")
        movie.box_office = request.POST.get("box_office")
        movie.poster_url = request.POST.get("poster_url")
        movie.save()

        messages.success(request, f"Movie '{movie.title}' updated successfully.")
        return redirect("manage_movies")

    return render(request, "custom_admin/edit_movie.html", {"movie": movie})

@admin_required
def delete_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":
        movie.delete()
        messages.success(request, f"Movie '{movie.title}' deleted successfully.")
        return redirect("manage_movies")

    return redirect("edit_movie", movie_id=movie_id)
