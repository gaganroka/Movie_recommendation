from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from movies.models.movie_model import *  #Import the model
from movies.models.auth_model import UserProfile  # ✅ Import UserProfile
from movies.models.admin_model import AdminUser

# ✅ Register Movie Model


class UserProfileAdmin(admin.ModelAdmin):
    """Custom admin panel for UserProfile"""
    list_display = ("user", "full_name", "contact", "profile_photo")  # ✅ Show these columns in admin
    search_fields = ("user__username", "full_name", "contact")

# ✅ Register UserProfile instead of CustomUser
admin.site.register(UserProfile, UserProfileAdmin)

admin.site.register(Movie)  # Register the model in Django Admin
admin.site.register(Review)
admin.site.register(Favorite)
admin.site.register(AdminUser)




