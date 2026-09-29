from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from movies.models.admin_model import AdminUser
from movies.models.movie_model import Movie, Review
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from movies.models.admin_session_model import AdminAuthSession
import secrets

# 🔐 Decorator to protect all admin routes
# Uses separate AdminAuthSession table, NOT Django session

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Check admin session from cookie/header, NOT Django session
        admin_cookie = request.COOKIES.get('admin_session_key')
        if admin_cookie:
            try:
                session = AdminAuthSession.objects.get(session_key=admin_cookie, is_active=True)
                # Store admin info in request for this request only
                request.admin_session = session
            except AdminAuthSession.DoesNotExist:
                request.admin_session = None
        else:
            request.admin_session = None

        if not request.admin_session:
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_admin_session(request):
    cookie = request.COOKIES.get('admin_session_key')
    if cookie:
        try:
            return AdminAuthSession.objects.get(session_key=cookie, is_active=True)
        except AdminAuthSession.DoesNotExist:
            return None
    return None


# ✅ Admin Login - Uses separate session table

def admin_login(request):
    print("🔥 ADMIN LOGIN VIEW HIT")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin_user = AdminUser.objects.get(username=username)
            if check_password(password, admin_user.password):
                # Create SEPARATE admin session (independent from Django session)
                session_key = secrets.token_hex(20)
                AdminAuthSession.objects.create(
                    session_key=session_key,
                    admin_user_id=admin_user.id
                )
                response = redirect("admin_dashboard")
                # Set admin cookie - separate from Django's session cookie
                response.set_cookie('admin_session_key', session_key, max_age=86400*7, httponly=True)
                # No message needed — redirect takes user directly to dashboard
                return response
            else:
                messages.error(request, "Incorrect password.")
        except AdminUser.DoesNotExist:
            messages.error(request, "Admin user not found.")

    return render(request, "custom_admin/login.html")


# 🚪 Admin Logout - Only removes admin cookie/session

def admin_logout(request):
    # Accept GET (navbar link) or POST (sidebar button) — both clear session
    cookie = request.COOKIES.get('admin_session_key')
    if cookie:
        AdminAuthSession.objects.filter(session_key=cookie).update(is_active=False)
    response = redirect('admin_login')
    response.delete_cookie('admin_session_key')
    return response


# 🏠 Admin Dashboard
@admin_required
def admin_dashboard(request):
    admin_session = request.admin_session
    admin_user = AdminUser.objects.get(id=admin_session.admin_user_id)

    return render(request, "custom_admin/dashboard.html", {
        "admin_user": admin_user,
        "total_users": User.objects.count(),
        "total_movies": Movie.objects.count(),
        "total_reviews": Review.objects.count(),
    })

@admin_required
def manage_users(request):
    users = User.objects.all().order_by("id")
    return render(request, "custom_admin/users.html", {"users": users})

# 🎬 Manage Movies
@admin_required
def manage_movies(request):
    all_movies = Movie.objects.all()
    paginator = Paginator(all_movies, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "custom_admin/movies.html", {"movies": page_obj})

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
                title=title, year=year, genre=genre, director=director,
                actors=actors, plot=plot, imdb_rating=imdb_rating,
                imdb_votes=imdb_votes, box_office=box_office, poster_url=poster_url
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
