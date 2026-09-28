from django.db import models
from .auth_model import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField()
    genre = models.TextField()
    director = models.TextField()
    actors = models.TextField()
    plot = models.TextField()
    imdb_rating = models.FloatField()
    imdb_votes = models.CharField(max_length=50, blank=True, null=True)
    box_office = models.CharField(max_length=50, blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating}⭐)"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey("Movie", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")  # ✅ Prevents duplicate favorites

    def __str__(self):
        return f"{self.user.username} ❤️ {self.movie.title}"