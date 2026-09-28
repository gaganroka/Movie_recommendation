import pandas as pd
from django.core.management.base import BaseCommand
from movies.models.movie_model import Movie

class Command(BaseCommand):
    help = "Add new movies from CSV to the database without duplicates"

    def handle(self, *args, **kwargs):
        # Load existing movies from the database
        existing_titles = set(Movie.objects.values_list("title", flat=True))

        # Load updated dataset from CSV
        csv_file = "top_1000_hollywood_movies_omdb.csv"
        df = pd.read_csv(csv_file)

        new_movies = []
        for _, row in df.iterrows():
            title = row["Title"]

            # Extract first year if it's a range (e.g., "2014–2015" → "2014")
            try:
                year = int(str(row["Year"]).split("–")[0])
            except ValueError:
                year = None

            # Assign default IMDb rating of 4.0 if missing
            imdb_rating = float(row["IMDb Rating"]) if pd.notna(row["IMDb Rating"]) else 4.0

            # Only add new movies that aren't already in the database
            if title not in existing_titles and year is not None:
                new_movies.append(Movie(
                    title=row["Title"],
                    year=year,
                    genre=row["Genre"],
                    director=row["Director"],
                    actors=row["Actors"],
                    plot=row["Plot"],
                    imdb_rating=imdb_rating,  # ✅ Defaults to 4.0 if missing
                    imdb_votes=row.get("IMDb Votes", ""),
                    box_office=row.get("Box Office", ""),
                    poster_url=row.get("Poster URL", "")
                ))

        # Bulk insert new movies
        if new_movies:
            Movie.objects.bulk_create(new_movies)
            self.stdout.write(self.style.SUCCESS(f"Successfully added {len(new_movies)} new movies!"))
        else:
            self.stdout.write(self.style.WARNING("No new movies to add. Database is already up to date."))
