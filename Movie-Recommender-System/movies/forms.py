from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from movies.models.auth_model import UserProfile 
from movies.models.movie_model import *

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=False)
    contact = forms.CharField(max_length=20, required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User  # ✅ Use Django's default User model
        fields = ["username", "email", "password1", "password2", "full_name", "contact", "profile_photo"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": self.cleaned_data["full_name"],
                    "contact": self.cleaned_data["contact"],
                    "profile_photo": self.cleaned_data.get("profile_photo"),
                },
            )
        return user

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} ⭐") for i in range(1, 6)], attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-input", "placeholder": "Write your review..."}),
        }