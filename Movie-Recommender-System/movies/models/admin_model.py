from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Custom manager (required when using AbstractBaseUser)
class AdminUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self.create_user(username, password, **extra_fields)

# Actual model
class AdminUser(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to="admin_photos/", blank=True, null=True, default="admin_photos/default.jpg")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Optional, for admin panel use
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = AdminUserManager()

    def __str__(self):
        return self.username
