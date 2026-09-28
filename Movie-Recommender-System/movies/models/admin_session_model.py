from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class AdminAuthSession(models.Model):
    """Separate session store for admin authentication - fully independent from Django auth"""
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    admin_user_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Admin session for admin {self.admin_user_id}"
