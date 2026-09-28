from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    """Extends Django's default User model with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    full_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True, default="profile_photos/default.jpg")

    def __str__(self):
        return self.user.username
    

