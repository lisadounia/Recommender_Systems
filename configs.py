# local imports
from models import *


class EvalConfig:
    
    models = [
      #------------------------------------- User based -------------------------------------------
      #("KNN_k=5_msd", UserBased, {"engine": "knn", "k": 5, "min_k": 2, "sim_options": {"name": "msd", "user_based": True, "min_support": 3}}),
      #("KNN_k=10_msd", UserBased, {"engine": "knn", "k": 10, "min_k": 2, "sim_options": {"name": "msd", "user_based": True, "min_support": 3}}),
    ("KNN_k=50_msd", UserBased, {"engine": "knn", "k": 50, "min_k": 2, "sim_options": {"name": "msd", "user_based": True, "min_support": 3}}),
      #("KNN_k=100_msd", UserBased, {"engine": "knn", "k": 100, "min_k": 2, "sim_options": {"name": "msd", "user_based": True, "min_support": 3}}),
      #("UserBased_k=5_jaccard", UserBased, {"engine": "custom", "k": 5, "min_k": 2, "sim_options": {"name": "jaccard", "user_based": True, "min_support": 3}}),
      #("UserBased_k=10_jaccard", UserBased, {"engine": "custom", "k": 10, "min_k": 2, "sim_options": {"name": "jaccard", "user_based": True, "min_support": 3}}),
      #("UserBased_k=50_jaccard", UserBased, {"engine": "custom", "k": 50, "min_k": 2, "sim_options": {"name": "jaccard", "user_based": True, "min_support": 3}}),
      #("UserBased_k=100_jaccard", UserBased, {"engine": "custom", "k": 100, "min_k": 2, "sim_options": {"name": "jaccard", "user_based": True, "min_support": 3}})
 
      #------------------------------------- Content based -------------------------------------------
    #  ("LinearRegression", ContentBased, {"features_method": "title_length", "regressor_method": "linear_regression"}),
    #  ("LinearRegression", ContentBased, {"features_method": "date", "regressor_method": "linear_regression"}),
     # ("LinearRegression", ContentBased, {"features_method": "mixed-features", "regressor_method": "linear_regression"}),
     #("LinearRegression", ContentBased, {"features_method": "genome-top-tags", "regressor_method": "linear_regression"}),
     # ("Genome",ContentBased, {"features_method" : "mixed-features", "regressor_method": "linear_regression"}),
     #("GradientBoosting", ContentBased, {"features_method": "tfidf_genres","regressor_method": "gradient_boosting"}),
     # ("RandomForest", ContentBased, {"features_method": "visual", "regressor_method": "random_forest"}),
     # ("GradientBoosting", ContentBased, {"features_method": "date+visual+genres", "regressor_method": "gradient_boosting"}),
      #("KNNRegressor", ContentBased, {"features_method": "visual", "regressor_method": "knn_regressor"}), 
      #("LinearRegression", ContentBased, {"features_method": "date+visual+genres", "regressor_method":  "linear_regression"}),
      #("Ridge",ContentBased, {"features_method" : "mixed-features", "regressor_method": "ridge_regression"}),
      #("Ridge450lsqr",ContentBased_cleaned, {"features_method" : "mixed-features", "regressor_method": "ridge_regression"}),
      
      #------------------------------------- latent based -------------------------------------------
      #("SVD_Optimized", ModelSVDOptimized, {}),
]

    split_metrics = ["mae","rmse"]

    loo_metrics = ["hit_rate"]
    full_metrics = ["novelty"]

    # Split parameters
    test_size = 0.25  # -- configure the test_size (from 0 to 1) --

    # Loo parameters
    top_n_value = 40  # -- configure the numer of recommendations (> 1) --
