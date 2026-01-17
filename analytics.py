import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import coo_matrix
from scipy.sparse import csr_matrix
from constants import Constant as C

def compute_content_stats(df_items):
    n_movies = df_items[C.ITEM_ID_COL].nunique()

    years = df_items[C.LABEL_COL].str.extract(r'\((\d{4})\)')[0].dropna().astype(int)
    min_year = years.min()
    max_year = years.max()
    
    genres = set()
    df_items[C.GENRES_COL].dropna().apply(lambda x: genres.update(x.split('|')))
    
    print(f"Number of films: {n_movies}")
    print(f"Period covered: {min_year} - {max_year}")
    print(f"Genres present: {sorted(genres)}")


def compute_ratings_stats(df_ratings, df_items, write=True):
    total_ratings = len(df_ratings)
    unique_users = df_ratings[C.USER_ID_COL].nunique()
    unique_movies = df_ratings[C.ITEM_ID_COL].nunique()

    rating_counts = df_ratings[C.ITEM_ID_COL].value_counts()
    most_rated = rating_counts.max()
    least_rated = rating_counts.min()
    
    rating_values = sorted(df_ratings[C.RATING_COL].unique())
    unrated_movies = set(df_items[C.ITEM_ID_COL]) - set(df_ratings[C.ITEM_ID_COL])
    
    stats = {
        'Total number of ratings given': total_ratings,
        'Number of distinct users who rated': unique_users,
        'Number of distinct movies that received at least one rating': unique_movies,
        'Highest number of ratings received by a single movie': most_rated,
        'Lowest number of ratings received by a movie': least_rated,
        'All possible rating values used': rating_values,
        'Number of movies that received no rating at all': len(unrated_movies)
    }
    if write == True : 
        for k, v in stats.items():
            print(f"{k}: {v}")

    return  unique_users, unique_movies



def plot_long_tail(df_ratings):
    rating_counts = df_ratings[C.ITEM_ID_COL].value_counts()
    rating_counts_sorted = rating_counts.sort_values(ascending=False).reset_index(drop=True)
    plt.figure(figsize=(10, 6))
    plt.plot(rating_counts_sorted.values, linewidth=1)
    plt.title('Long-tail distribution of rating frequencies')
    plt.xlabel('Movies (sorted by number of ratings)')
    plt.ylabel('Number of ratings')
    plt.grid(True)
    plt.tight_layout()
    plt.show()




def compute_sparsity(df_ratings, n_users, n_movies):
    density = len(df_ratings) / (n_users * n_movies)
    return 1 - density

def create_X(df):
    """
    Generates a sparse matrix from ratings dataframe and displays sparsity.

    Args:
        df: pandas dataframe containing 3 columns (userId, movieId, rating)

    Returns:
        X: sparse matrix
        user_mapper: dict that maps user id's to user indices
        user_inv_mapper: dict that maps user indices to user id's
        movie_mapper: dict that maps movie id's to movie indices
        movie_inv_mapper: dict that maps movie indices to movie id's
    """
    M = df['userId'].nunique()
    N = df['movieId'].nunique()

    user_mapper = dict(zip(np.unique(df["userId"]), list(range(M))))
    movie_mapper = dict(zip(np.unique(df["movieId"]), list(range(N))))

    user_inv_mapper = dict(zip(list(range(M)), np.unique(df["userId"])))
    movie_inv_mapper = dict(zip(list(range(N)), np.unique(df["movieId"])))

    user_index = [user_mapper[i] for i in df['userId']]
    item_index = [movie_mapper[i] for i in df['movieId']]

    X = csr_matrix((df["rating"], (user_index, item_index)), shape=(M, N))

    # ➤ Affichage de la sparsité
    max_users = min(100, M)
    max_items = min(100, N)
    plt.figure(figsize=(6, 6))
    plt.spy(X[:max_users, :max_items], markersize=1)
    plt.title(f"Sparsity pattern ({max_users} users × {max_items} movies)")
    plt.xlabel("Movies")
    plt.ylabel("Users")
    plt.show()

    return X, user_mapper, movie_mapper, user_inv_mapper, movie_inv_mapper
