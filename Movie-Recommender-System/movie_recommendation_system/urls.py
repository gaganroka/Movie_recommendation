"""
URL configuration for movie_recommendation_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from movies.views.home_view import *
from movies.views.auth_view import *
from movies.views.profile_view import *
from movies.views.admin_view import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home_view, name="home"),
    path("movie/<int:movie_id>/", movie_detail, name="movie_detail"),
    path("search/", live_search, name="live_search"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("movie/<int:movie_id>/review/", submit_review, name="submit_review"),
    path("toggle_favorite/<int:movie_id>/", toggle_favorite, name="toggle_favorite"),
    path("profile/", profile_view, name="profile"),
    path("profile/settings/", settings_view, name="settings"),
    path("profile/change-password/", change_password, name="change_password"),

    path("admin-panel/login/", admin_login, name="admin_login"),
    path("admin-panel/", admin_dashboard, name="admin_dashboard"),
    path("admin-panel/logout/", admin_logout, name="admin_logout"),
    path("admin-panel/users/", manage_users, name="manage_users"),
    path("admin-panel/movies/", manage_movies, name="manage_movies"),
    path("admin-panel/reviews/", manage_reviews, name="manage_reviews"),
    path("admin-panel/movies/add/", add_movie, name="add_movie"),
    path("admin-panel/movies/edit/<int:movie_id>/", edit_movie, name="edit_movie"),
    path("admin-panel/movies/delete/<int:movie_id>/", delete_movie, name="delete_movie"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
