from django.apps import AppConfig


class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'

    # Importing the model
    def ready(self):
        from movies.models import movie_model  # Ensure model is loaded
