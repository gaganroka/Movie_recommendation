import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from movies.models.movie_model import *

# ✅ Function to prepare the dataset and calculate similarity
def build_movie_similarity_matrix():
    """Creates a TF-IDF-based similarity matrix for movie recommendations."""

    # ✅ Fetch all movies from the database
    movies = Movie.objects.all()

    # ✅ Convert to a Pandas DataFrame
    data = pd.DataFrame(list(movies.values("id", "title", "genre", "director", "actors", "plot")))

    # ✅ Combine text features into a single column
    data["combined_features"] = data["genre"] + " " + data["director"] + " " + data["actors"] + " " + data["plot"]

    # ✅ Convert missing values to empty strings
    data.fillna("", inplace=True)

    # ✅ Use TF-IDF Vectorizer to transform the text
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data["combined_features"])

    # ✅ Compute cosine similarity between movies
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    return data, similarity_matrix

# ✅ Function to get movie recommendations
def get_similar_movies(movie_id, data, similarity_matrix, num_recommendations=10):
    """Returns a list of similar movies based on the given movie ID."""
    
    if movie_id not in data["id"].values:
        return []

    # ✅ Find the index of the movie in the DataFrame
    movie_index = data[data["id"] == movie_id].index[0]

    # ✅ Get similarity scores for the movie
    similarity_scores = list(enumerate(similarity_matrix[movie_index]))

    # ✅ Sort by similarity score (highest first) & exclude the movie itself
    sorted_movies = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:num_recommendations + 1]

    # ✅ Get recommended movie IDs
    recommended_movie_ids = [data.iloc[i[0]]["id"] for i in sorted_movies]

    return Movie.objects.filter(id__in=recommended_movie_ids)

def build_user_movie_matrix():
    """Create a User-Movie matrix where each cell represents if a user favorited a movie."""
    
    favorites = Favorite.objects.select_related("user", "movie")
    
    data = []
    for fav in favorites:
        data.append((fav.user.id, fav.movie.id))  # (user_id, movie_id)
    
    df = pd.DataFrame(data, columns=["user_id", "movie_id"])
    
    # ✅ Convert to matrix (rows = movies, columns = users)
    user_movie_matrix = df.pivot_table(index="movie_id", columns="user_id", aggfunc=len, fill_value=0)
    
    return user_movie_matrix

def get_similar_users(user_id, user_movie_matrix):
    """Find users similar to the given user based on their favorite movies."""
    
    if user_id not in user_movie_matrix.columns:
        return []
    
    # ✅ Compute similarity with all users
    user_similarities = cosine_similarity(user_movie_matrix.T)
    
    # ✅ Convert to a DataFrame
    similarity_df = pd.DataFrame(user_similarities, index=user_movie_matrix.columns, columns=user_movie_matrix.columns)
    
    # ✅ Sort users by similarity (excluding the user itself)
    similar_users = similarity_df[user_id].drop(index=user_id).sort_values(ascending=False)
    
    return similar_users.index.tolist()

def recommend_movies_for_user(user_id, num_recommendations=10):
    """Recommend movies for a user based on similar users' preferences."""
    
    user_movie_matrix = build_user_movie_matrix()
    
    # ✅ Get similar users
    similar_users = get_similar_users(user_id, user_movie_matrix)
    
    if not similar_users:
        return Movie.objects.order_by("?")[:num_recommendations]  # Return random movies if no similar users found
    
    # ✅ Get movies favorited by similar users
    similar_users_movies = user_movie_matrix[similar_users].sum(axis=1)
    
    # ✅ Exclude movies the current user has already favorited
    user_movies = set(Favorite.objects.filter(user_id=user_id).values_list("movie_id", flat=True))
    recommended_movies = [Movie.objects.get(id=movie_id) for movie_id in similar_users_movies.index if movie_id not in user_movies]
    
    return recommended_movies[:num_recommendations]  # Return top recommendations
